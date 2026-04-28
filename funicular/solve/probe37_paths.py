#!/usr/bin/env python3
"""
probe37: brute-force hidden HTTP paths under /api/operator/*.
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

PATHS = [
    "/api/operator/maintenance-preview",
    "/api/operator/plc-sync",
    "/api/operator/telemetry-snapshot",
    "/api/operator/regulatory",
    "/api/operator/regulation",
    "/api/operator/verify",
    "/api/operator/auth",
    "/api/operator/authorize",
    "/api/operator/authenticate",
    "/api/operator/handshake",
    "/api/operator/login",
    "/api/operator/init",
    "/api/operator/recovery",
    "/api/operator/restore",
    "/api/operator/packet",
    "/api/operator/gateway",
    "/api/operator/session",
    "/api/operator/mode",
    "/api/operator/check",
    "/api/operator/preview",
    "/api/operator/snapshot",
    "/api/operator/sync",
    "/api/operator/health",
    "/api/operator/state",
    "/api/operator/status",
    "/api/operator/ping",
    "/api/operator/info",
    "/api/operator/me",
    "/api/operator/who",
    "/api/operator/cmd",
    "/api/operator/command",
    "/api/operator/exec",
    "/api/operator/admin",
    "/api/operator/list",
    "/api/operator/all",
    "/api/operator/tasks",
    "/api/operator/queue",
    "/api/operator/journal",
    "/api/operator/log",
    "/api/operator/logs",
    "/api/operator/upload",
    "/api/operator/file",
    "/api/operator/files",
    "/api/operator/backup",
    "/api/operator/backups",
    "/api/operator/dispatch/restore",
    "/api/operator/dispatch/auth",
    "/api/operator/dispatch/preview",
    # api root paths
    "/api/restore",
    "/api/recovery",
    "/api/auth",
    "/api/admin",
    "/api/login",
    "/api/health",
    "/api/state",
    "/api/info",
    "/api/me",
    "/api/internal",
    "/api/v1/operator/dispatch",
    "/api/v2/operator/dispatch",
    "/api/operator",
    "/api/operator/",
    # short paths
    "/restore",
    "/recovery",
    "/auth",
    "/admin",
    "/login",
    "/internal",
    "/system",
    "/operator/restore",
    "/operator/recovery",
    "/operator/auth",
    "/operator/admin",
    "/engineer",
    "/service",
    "/maintenance",
]


def call(method, path, body=None, ct="application/json"):
    url = f"https://{HOST}{path}"
    data = body.encode() if body else None
    headers = {"User-Agent": "p37"}
    if data:
        headers["Content-Type"] = ct
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=10) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data
    except Exception as e:
        return -1, {}, str(e).encode()


# POST {} JSON
print("# POST {} application/json")
for path in PATHS:
    st, h, body = call("POST", path, "{}", "application/json")
    if st not in (404,):
        print(f"  POST {path:50s} st={st} len={len(body)} body={body[:80]!r}")
    time.sleep(0.15)

# GET
print("\n# GET")
for path in PATHS:
    st, h, body = call("GET", path)
    if st not in (404, 308):
        print(f"  GET  {path:50s} st={st} len={len(body)} body={body[:80]!r}")
    time.sleep(0.15)

# OPTIONS
print("\n# OPTIONS (only if 204/200)")
for path in PATHS:
    st, h, body = call("OPTIONS", path)
    if st in (200, 204):
        allow = h.get("Allow", h.get("allow", ""))
        print(f"  OPT  {path:50s} st={st} allow={allow}")
    time.sleep(0.15)

print("\n# done.")
