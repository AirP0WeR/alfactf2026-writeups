#!/usr/bin/env python3
"""Save responses and diff bytewise."""
import urllib.request, urllib.error, ssl, http.cookiejar

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def req(method, url, headers=None, body=None):
    r = urllib.request.Request(url, data=body, method=method, headers=headers or {})
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


_, _, get_body = req("GET", URL)
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
_, _, post_body = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)

open("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/get.html", "wb").write(get_body)
open("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/post_actionid.html", "wb").write(post_body)
print("saved", len(get_body), len(post_body))
print("identical?", get_body == post_body)

# Diff
import difflib
g = get_body.decode("utf-8", "replace")
p = post_body.decode("utf-8", "replace")
diff = list(difflib.unified_diff(g.split("><"), p.split("><"), lineterm="", n=2))
print(f"diff lines: {len(diff)}")
for l in diff[:80]:
    print(l)
