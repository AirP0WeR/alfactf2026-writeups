#!/usr/bin/env python3
"""
probe34: cookie persistence + Cyrillic terminal.

Hypothesis: dispatch (даже с 502) ставит server-side state per-session.
Action checks cookie. Все прежние probes посылали terminal="OP-3" (latin),
но в props сидит "ОП-3 / верхняя станция" (Cyrillic).
"""
import socket
import ssl
import struct
import time
import re
import json
import urllib.request
import urllib.error
from hpack import Encoder, Decoder

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


def call_action(body_bytes, cookie=None, content_type="text/plain;charset=UTF-8", extra=None):
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
        ("user-agent", "p34"),
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
    dec = Decoder()
    status = None
    set_cookies = []
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
                    if sk.lower() == "set-cookie":
                        set_cookies.append(sv)
            except Exception:
                pass
        elif ftype == 0:
            data = payload
            if flags & 0x8:
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            body += data
    return status, headers_out, body, set_cookies


def extract_row1(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'^1:(\{.*?\})$', text, re.MULTILINE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return m.group(1)
    return None


def call_dispatch(operation, packet="south-line.2026-03-27", workOrder="WO-17-04", terminal="OP-3", cookie=None):
    """Call /api/operator/dispatch via urllib. Return (status, headers_dict, body, set_cookies)."""
    url = f"https://{HOST}/api/operator/dispatch"
    body = json.dumps({
        "operation": operation,
        "packet": packet,
        "workOrder": workOrder,
        "terminal": terminal,
    }).encode()
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "p34",
    }
    if cookie:
        req_headers["Cookie"] = cookie
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    set_cookies = []
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
            for k, v in resp.headers.items():
                if k.lower() == "set-cookie":
                    set_cookies.append(v)
            return resp.status, dict(resp.headers), resp.read(), set_cookies
    except urllib.error.HTTPError as e:
        for k, v in e.headers.items():
            if k.lower() == "set-cookie":
                set_cookies.append(v)
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data, set_cookies


def get_initial_cookie():
    """GET / and pull station_sid cookie."""
    url = f"https://{HOST}/"
    req = urllib.request.Request(url, headers={"User-Agent": "p34"})
    with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
        cookies = []
        for k, v in resp.headers.items():
            if k.lower() == "set-cookie":
                cookies.append(v)
        sid = None
        for c in cookies:
            m = re.match(r'station_sid=([^;]+)', c)
            if m:
                sid = m.group(1)
                break
        return sid, cookies


CYRILLIC_TERMINAL_FULL = "ОП-3 / верхняя станция"
CYRILLIC_TERMINAL_SHORT = "ОП-3"
LATIN_TERMINAL = "OP-3"


print("\n## Step 0: Initial cookie")
init_sid, init_set_cookies = get_initial_cookie()
print(f"  initial station_sid = {init_sid}")
print(f"  set-cookies on GET /: {init_set_cookies}")

print("\n## Step 1: Action with INITIAL session cookie ONLY (baseline)")
cookie = f"station_sid={init_sid}" if init_sid else None
st, _, body, _ = call_action(b'["$K1"]', cookie=cookie)
row1 = extract_row1(body)
print(f"  status={st} row1={row1}")

print("\n## Step 2: Dispatch with each cyrillic/latin terminal, then action with same cookie")
for op in ["maintenance-preview", "plc-sync", "telemetry-snapshot"]:
    for term in [CYRILLIC_TERMINAL_FULL, CYRILLIC_TERMINAL_SHORT, LATIN_TERMINAL]:
        # fresh session
        sid, _ = get_initial_cookie()
        cook = f"station_sid={sid}"
        d_st, d_h, d_body, d_sc = call_dispatch(op, terminal=term, cookie=cook)
        # Check if dispatch refreshed cookie
        new_sid = None
        for c in d_sc:
            m = re.match(r'station_sid=([^;]+)', c)
            if m:
                new_sid = m.group(1)
        # Action with original cook
        a_st, _, a_body, _ = call_action(b'["$K1"]', cookie=cook)
        row1 = extract_row1(a_body)
        err = row1.get("error") if isinstance(row1, dict) else None
        msg = (row1.get("message") if isinstance(row1, dict) else "")[:60] if row1 else ""
        same_sid = (new_sid == sid) if new_sid else "no-set"
        print(f"  op={op:22s} term={term[:25]:25s} d_st={d_st} sid_eq={same_sid} a_st={a_st} err={err} msg={msg!r}")
        time.sleep(0.4)

print("\n## Step 3: Multi-dispatch then action (state accumulation)")
sid, _ = get_initial_cookie()
cook = f"station_sid={sid}"
print(f"  using sid={sid}")
for i in range(4):
    for op in ["maintenance-preview", "plc-sync", "telemetry-snapshot"]:
        d_st, _, _, _ = call_dispatch(op, terminal=CYRILLIC_TERMINAL_FULL, cookie=cook)
        time.sleep(0.3)
    a_st, _, a_body, _ = call_action(b'["$K1"]', cookie=cook)
    row1 = extract_row1(a_body)
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = (row1.get("message") if isinstance(row1, dict) else "")[:60] if row1 else ""
    print(f"  iter#{i} action: st={a_st} err={err} msg={msg!r}")
    time.sleep(0.5)

print("\n## Step 4: Dispatch with ALL THREE ops in sequence, then action")
sid, _ = get_initial_cookie()
cook = f"station_sid={sid}"
for op in ["maintenance-preview", "plc-sync", "telemetry-snapshot"]:
    for term in [CYRILLIC_TERMINAL_FULL]:
        for pkt_var in ["south-line.2026-03-27", "south-line.2026-03-27.bak", "WO-17-04"]:
            d_st, _, _, _ = call_dispatch(op, packet=pkt_var, terminal=term, cookie=cook)
            time.sleep(0.2)
a_st, _, a_body, _ = call_action(b'["$K1"]', cookie=cook)
row1 = extract_row1(a_body)
print(f"  After 3-op×3-pkt warmup: row1={row1}")

print("\n## Step 5: Same-cookie action WITHOUT any dispatch (control)")
sid, _ = get_initial_cookie()
cook = f"station_sid={sid}"
a_st, _, a_body, _ = call_action(b'["$K1"]', cookie=cook)
row1 = extract_row1(a_body)
print(f"  Control (no dispatch): row1={row1}")

print("\n## Step 6: Dispatch+action with NO cookie, NO new cookie passing")
a_st, _, a_body, _ = call_action(b'["$K1"]', cookie=None)
row1 = extract_row1(a_body)
print(f"  Action no-cookie: row1={row1}")

print("\n# done.")
