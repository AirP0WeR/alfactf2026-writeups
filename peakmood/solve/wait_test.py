#!/usr/bin/env python3
"""
Test if wait-time between scans affects the tier. Open a session, scan once
to start the clock, then wait N seconds, then scan and see what tier appears.
"""
import json, time, ssl, urllib.request, urllib.error, sys

BASE = "https://peakmood-ou1mhzjv.alfactf.ru"
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def post(path, payload, token=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try: return e.code, json.loads(body)
        except: return e.code, {"raw": body}


def open_session(device_id):
    s, body = post("/api/v1/session/open", {
        "device_id": device_id, "client_version": "1.0.0", "model": "x",
    })
    return body["session_token"]


def scan(token, lat=55.7558, lon=37.6176, alt=180.0):
    s, body = post("/api/v1/geo/update", {
        "lat": lat, "lon": lon,
        "reported_alt_m": alt, "vertical_accuracy_m": 0.0,
    }, token)
    return body


def hit(token, nid):
    return post("/api/v1/node/hit", {"node_id": nid}, token)


def open_node(token, nid):
    return post("/api/v1/node/open", {"node_id": nid}, token)


def harvest(label, wait_seconds, lat=55.7558, lon=37.6176, alt=180.0, dev=None):
    dev = dev or f"wait-test-{wait_seconds}-{int(time.time())}"
    tok = open_session(dev)
    print(f"\n=== {label}: wait={wait_seconds}s, alt={alt}m ===")
    print(f"    device_id={dev}")
    # initial scan to establish the session
    print(f"    [{time.strftime('%H:%M:%S')}] initial scan")
    body = scan(tok, lat, lon, alt)
    sc = body.get("scan", {})
    print(f"    -> tier={sc.get('tier')!r}, node={'YES' if sc.get('node') else 'no'}")

    print(f"    [{time.strftime('%H:%M:%S')}] sleeping {wait_seconds}s ...")
    time.sleep(wait_seconds)

    print(f"    [{time.strftime('%H:%M:%S')}] post-wait scan")
    # Move slightly so the geo reading is definitely 'fresh'
    body = scan(tok, lat + 0.0005, lon + 0.0005, alt)
    sc = body.get("scan", {})
    n = sc.get("node")
    print(f"    -> tier={sc.get('tier')!r}, name={sc.get('display_name')!r}, node={'YES' if n else 'no'}")
    if n:
        print(f"    node: {json.dumps(n, ensure_ascii=False)}")
        nid = n["id"]
        for _ in range(n["hits_left"]):
            hit(tok, nid)
        s, ob = open_node(tok, nid)
        print(f"    open: {json.dumps(ob, ensure_ascii=False)}")
        return ob
    return None


if __name__ == "__main__":
    waits = [int(x) for x in sys.argv[1:]] or [0, 30, 60, 120, 300]
    for w in waits:
        harvest(f"wait_{w}s", w)
