#!/usr/bin/env python3
"""
probe39: GET / with various next-router-state-tree headers and RSC headers.
"""
import json
import ssl
import time
import urllib.request
import urllib.error
import hashlib

HOST = "funicular-gm2cxozn.alfactf.ru"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(path, headers=None):
    url = f"https://{HOST}{path}"
    req_headers = {"User-Agent": "p39"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers, method="GET")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=15) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data


# Baseline
print("# baseline GET /")
st, h, body = get("/")
base_sha = hashlib.sha256(body).hexdigest()[:16]
print(f"  st={st} len={len(body)} sha={base_sha}")

print("\n# RSC=1 (would dump RSC payload)")
st, h, body = get("/", {"RSC": "1"})
print(f"  st={st} len={len(body)} sha={hashlib.sha256(body).hexdigest()[:16]} ct={h.get('Content-Type', '')}")
if b"$F" in body or b"$@" in body or len(body) < 5000:
    print(f"    body[:500]={body[:500]!r}")

print("\n# different next-router-state-tree variants")
TREES = [
    '["",{"children":["__PAGE__",{}]}]',
    '["",{"children":["__PAGE__",{}]},null,null,true]',
    '["",{"children":["admin",{}]}]',
    '["",{"children":["recovery",{}]}]',
    '["",{"children":["restore",{}]}]',
    '["",{"children":["operator",{"children":["restore",{}]}]}]',
    '["",{"children":["operator",{"children":["recovery",{}]}]}]',
    '["",{"children":["operator",{"children":["__PAGE__",{}]}]}]',
    '["",{"children":["api",{"children":["operator",{"children":["dispatch",{}]}]}]}]',
    '["",{"children":["@modal",{"children":["restore",{}]}]}]',
    '["restore",{"children":["__PAGE__",{}]}]',
]

for tree in TREES:
    st, h, body = get("/", {"RSC": "1", "Next-Router-State-Tree": tree})
    sha = hashlib.sha256(body).hexdigest()[:16]
    is_diff = sha != base_sha
    marker = " [DIFF]" if is_diff else ""
    label = tree[:60]
    print(f"  tree={label:<60} st={st} sha={sha} len={len(body)}{marker}")
    if is_diff and len(body) < 3000:
        print(f"    body={body!r}")
    time.sleep(0.3)

print("\n# Try cache poisoning: same URL twice")
st1, h1, b1 = get("/")
st2, h2, b2 = get("/")
print(f"  GET#1 sha={hashlib.sha256(b1).hexdigest()[:16]} cf={h1.get('X-Nextjs-Cache', '')}")
print(f"  GET#2 sha={hashlib.sha256(b2).hexdigest()[:16]} cf={h2.get('X-Nextjs-Cache', '')}")

print("\n# Try GET / with Next-Action header in URL path (cache key tampering)")
st, h, body = get("/?nextrouterstatetree=foo")
print(f"  ?nrst=foo: st={st} sha={hashlib.sha256(body).hexdigest()[:16]} len={len(body)}")

print("\n# Try GET on hidden segments")
for seg in ["/operator/restore", "/operator/recovery", "/operator/auth", "/operator/admin",
            "/restore", "/recovery", "/admin/restore", "/admin/recovery"]:
    st, h, body = get(seg)
    print(f"  GET {seg:30s} st={st} len={len(body)} cache={h.get('X-Nextjs-Cache', '')} ct={h.get('Content-Type', '')[:30]}")

print("\n# done.")
