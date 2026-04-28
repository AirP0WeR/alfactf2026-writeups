#!/usr/bin/env python3
"""
Action causes 503. Let's check:
1. Is the response 503 from lighttpd because Node died, OR is 503 the actual response from Node (intentional)?
2. Does the response itself ever contain the flag?
3. The previous tests with $ACTION_ID returned 200 with same page. But probe14 got 503. Why difference? Maybe state across runs.

Confirm by wait + retry with various forms.
"""
import urllib.request, urllib.error, ssl, time, hashlib

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(method, headers=None, body=None, timeout=30):
    r = urllib.request.Request(URL, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return None, {}, str(e).encode()


def multipart(fields):
    boundary = "----X1234ABC"
    parts = []
    for k, v in fields:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        parts.append(v.encode() if isinstance(v, str) else v)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return boundary, b"".join(parts)


def wait_until_up():
    for _ in range(30):
        s, _, _ = fetch("GET", timeout=10)
        if s == 200:
            return
        time.sleep(2)


# Confirm 200 first
s, _, _ = fetch("GET")
print("baseline GET", s)

# Trigger MPA
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
s, h, d = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body, timeout=20)
print(f"MPA action: status={s}, len={len(d)}, hash={hashlib.sha256(d).hexdigest()[:12]}")
print("body:", d[:400])
print("headers:", {k: v for k, v in h.items() if k.lower() in ('content-type', 'set-cookie', 'x-action', 'location', 'x-nextjs-redirect')})

# Wait for server to recover
print("\nwaiting for server to come back...")
wait_until_up()
print("OK back up")
