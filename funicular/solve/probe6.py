#!/usr/bin/env python3
"""Try legit dispatch operations and look for backup/restore hints in output."""
import urllib.request, urllib.error, ssl, json

URL = "https://funicular-gm2cxozn.alfactf.ru/api/operator/dispatch"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def post(url, body, headers=None):
    h = {"Content-Type": "application/json"}
    h.update(headers or {})
    r = urllib.request.Request(url, data=body, method="POST", headers=h)
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


for op in ("plc-sync", "telemetry-snapshot", "maintenance-preview"):
    payload = json.dumps({
        "operation": op,
        "packet": "south-line.2026-03-27",
        "workOrder": "WO-17-04",
        "terminal": "ОП-3 / верхняя станция"
    }).encode()
    s, h, d = post(URL, payload)
    print(f"\n=== {op} -> {s} ===")
    try:
        j = json.loads(d.decode())
        print(json.dumps(j, ensure_ascii=False, indent=2))
    except Exception:
        print(d.decode("utf-8", "replace")[:500])
