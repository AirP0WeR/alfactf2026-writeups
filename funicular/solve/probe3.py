#!/usr/bin/env python3
"""Compare GET vs POST $ACTION_ID response to see if anything changed."""
import urllib.request, ssl, difflib

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(method, headers=None, body=None):
    req = urllib.request.Request(URL, data=body, method=method, headers=headers or {})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


get = fetch("GET")
boundary = "----X1234ABC"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="$ACTION_ID_{ACTION_ID}"\r\n\r\n'
    f"\r\n--{boundary}--\r\n"
).encode()
post = fetch(
    "POST",
    {"Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "text/x-component"},
    body,
)
print("GET len", len(get), "POST len", len(post))
print("equal:", get == post)
diff = list(difflib.unified_diff(get.splitlines(), post.splitlines(), lineterm=""))
for line in diff[:50]:
    print(line)
