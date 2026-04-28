#!/usr/bin/env python3
"""
Detailed byte diff between GET and MPA POST. Use bytes-level inspection.
"""
import urllib.request, ssl

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(method, headers=None, body=None):
    r = urllib.request.Request(URL, data=body, method=method, headers=headers or {})
    with urllib.request.urlopen(r, context=ctx, timeout=30) as resp:
        return resp.read()


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


# Multiple GET to find dynamic parts
g1 = fetch("GET")
g2 = fetch("GET")
print("g1==g2:", g1 == g2, "len", len(g1), len(g2))

# Where do GETs differ?
for i, (a, b) in enumerate(zip(g1, g2)):
    if a != b:
        print(f"GET diff at {i}: a={g1[max(0,i-30):i+30]!r} b={g2[max(0,i-30):i+30]!r}")
        break

boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
p1 = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
p2 = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("\np1==p2:", p1 == p2, "len", len(p1), len(p2))
print("g1==p1:", g1 == p1)

# Also try with just any random POST without action
random_post = fetch("POST", {"Content-Type": "multipart/form-data; boundary=X"}, b"--X--\r\n")
print("\nrandom_post len", len(random_post))
print("g1==random_post:", g1 == random_post)
