#!/usr/bin/env python3
"""
Find the action effect by:
1. POST $ACTION_ID then GET, sharing cookies (action might set cookie/state)
2. POST $ACTION_REF with descriptor and look for any side-effect
3. Also try /api/operator/dispatch with operation:"recovery" / "restore" / "backup"
"""
import urllib.request, urllib.error, ssl, json, http.cookiejar

URL = "https://funicular-gm2cxozn.alfactf.ru/"
DISPATCH = URL + "api/operator/dispatch"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(cj),
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


# Step 1: GET to seed cookies
status, h, data = req("GET", URL)
print("INIT GET status", status, "cookies:", [c.name + "=" + c.value[:8] for c in cj])
print("INIT 'restored':", b'"restored":true' in data, b'"restored":false' in data)

# Step 2: POST $ACTION_ID
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
status, h, data = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print("\nPOST $ACTION_ID status", status, "len", len(data))
print("  cookies:", [c.name + "=" + c.value[:8] for c in cj])
print("  restored:true?", b'"restored":true' in data)
print("  setcookie?", h.get('Set-Cookie'))

# Step 3: GET with same cookie jar
status, h, data = req("GET", URL)
print("\nGET2 status", status, "len", len(data), "restored:true?", b'"restored":true' in data)

# Step 4: dispatch with various operations
for op in ("plc-restore", "restore", "recovery", "backup", "import-backup", "load-backup"):
    payload = json.dumps({"operation": op, "packet": "south-line.2026-03-27", "workOrder": "WO-17-04", "terminal": "ОП-3 / верхняя станция"}).encode()
    status, h, data = req("POST", DISPATCH, {"Content-Type": "application/json"}, payload)
    print(f"\nDISPATCH op={op!r} -> {status}")
    print("  body:", data[:500])
