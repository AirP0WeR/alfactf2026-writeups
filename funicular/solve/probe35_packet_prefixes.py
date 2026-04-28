#!/usr/bin/env python3
"""
probe35: try different packet prefixes / suffixes to find a "local fetch" path.
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


def call_dispatch(operation, packet="south-line.2026-03-27", workOrder="WO-17-04", terminal="ОП-3 / верхняя станция"):
    url = f"https://{HOST}/api/operator/dispatch"
    body = json.dumps({
        "operation": operation,
        "packet": packet,
        "workOrder": workOrder,
        "terminal": terminal,
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "p35",
    }, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
            data = resp.read()
            return resp.status, data, time.time() - t0
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, data, time.time() - t0
    except Exception as e:
        return -1, str(e).encode(), time.time() - t0


PREFIXES = [
    "backup", "cached", "replay", "local", "offline", "test", "mock", "dev",
    "file", "restore", "recovery", "last", "fallback", "snapshot", "archive",
    "fixture", "seed", "internal", "static", "preview",
]
SUFFIXES = [".bak", ".backup", ".cache", ".local", ".bin", ".tar", ".gz", ".old", ".restore"]
SPECIAL = [
    "south-line.2026-03-27",
    "WO-17-04",
    "05:44", "05:47", "05:56",
    "../south-line.2026-03-27",
    "south-line.2026-03-27/restore",
    "south-line.2026-03-27?recovery=1",
    "south-line",
    "default",
    "all",
    "*",
    "",
    "${packet}",
]

OPS = ["plc-sync", "telemetry-snapshot", "maintenance-preview"]

print("# probe35: prefix matrix")
results = []

# Baseline timing
for op in OPS:
    st, body, dt = call_dispatch(op)
    results.append((op, "south-line.2026-03-27", st, dt, body[:80]))
    print(f"  baseline op={op:20s} st={st} dt={dt:.2f}s body={body[:60]!r}")
    time.sleep(0.5)

print("\n# Prefix matrix (op=maintenance-preview):")
for prefix in PREFIXES:
    pkt = f"{prefix}:south-line.2026-03-27"
    st, body, dt = call_dispatch("maintenance-preview", packet=pkt)
    results.append(("maintenance-preview", pkt, st, dt, body[:80]))
    print(f"  pkt={pkt:50s} st={st} dt={dt:.2f}s body={body[:60]!r}")
    time.sleep(0.4)

print("\n# Suffix matrix:")
for suf in SUFFIXES:
    pkt = f"south-line.2026-03-27{suf}"
    st, body, dt = call_dispatch("maintenance-preview", packet=pkt)
    results.append(("maintenance-preview", pkt, st, dt, body[:80]))
    print(f"  pkt={pkt:50s} st={st} dt={dt:.2f}s body={body[:60]!r}")
    time.sleep(0.4)

print("\n# Special values:")
for spec in SPECIAL:
    pkt = spec
    st, body, dt = call_dispatch("maintenance-preview", packet=pkt)
    results.append(("maintenance-preview", pkt, st, dt, body[:80]))
    print(f"  pkt={pkt!r:50s} st={st} dt={dt:.2f}s body={body[:60]!r}")
    time.sleep(0.4)

print("\n# Try same matrix on plc-sync:")
for prefix in ["backup", "restore", "recovery", "local", "test"]:
    pkt = f"{prefix}:south-line.2026-03-27"
    st, body, dt = call_dispatch("plc-sync", packet=pkt)
    results.append(("plc-sync", pkt, st, dt, body[:80]))
    print(f"  op=plc-sync pkt={pkt:50s} st={st} dt={dt:.2f}s body={body[:60]!r}")
    time.sleep(0.4)

# Show all UNIQUE responses
print("\n## Unique status × len buckets:")
buckets = {}
for op, pkt, st, dt, body in results:
    key = (st, len(body), body[:40])
    buckets.setdefault(key, []).append((op, pkt, dt))
for key, items in buckets.items():
    st, ln, prev = key
    print(f"  st={st} len={ln} preview={prev!r:50s} count={len(items)}")
    for op, pkt, dt in items[:3]:
        print(f"    e.g. op={op} pkt={pkt!r} dt={dt:.2f}s")

print("\n# done.")
