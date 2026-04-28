#!/usr/bin/env python3
"""
PeakMood live recon. Open a session and scan in a loop, capturing every node
that appears, hit it down, open it, log loot. Goal: find what triggers FLAG tier.
"""
import json
import time
import ssl
import urllib.request
import urllib.error
import sys
import argparse

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
            body = r.read().decode()
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body}


def open_session(device_id="peakmood-static", client_version="1.0.0", model="static"):
    s, body = post("/api/v1/session/open", {
        "device_id": device_id,
        "client_version": client_version,
        "model": model,
    })
    return body["session_token"], body.get("player_tag")


def scan(token, lat, lon, alt, vacc=0.0):
    s, body = post("/api/v1/geo/update", {
        "lat": lat, "lon": lon,
        "reported_alt_m": alt, "vertical_accuracy_m": vacc,
    }, token)
    return s, body


def hit(token, node_id):
    return post("/api/v1/node/hit", {"node_id": node_id}, token)


def open_node(token, node_id):
    return post("/api/v1/node/open", {"node_id": node_id}, token)


def harvest_one(token, lat, lon, alt, label):
    """Scan until a node appears, then hit until ready, then open."""
    print(f"[*] {label}: scanning at lat={lat}, lon={lon}, alt={alt}")
    node = None
    drift = 0
    for i in range(200):
        # walk slightly to keep server happy with movement
        dlat = lat + drift * 0.0003
        dlon = lon + drift * 0.0003
        drift = (drift + 1) % 10
        s, body = scan(token, dlat, dlon, alt)
        sc = body.get("scan", {})
        n = sc.get("node")
        tier = sc.get("tier")
        msg = sc.get("display_name") or sc.get("message", "")
        print(f"    scan {i:>3} tier={tier!r:<10} node={'YES' if n else 'no':<3} {msg[:50]}")
        if n:
            node = n
            break
        time.sleep(2)
    if not node:
        print("[!] never saw a node")
        return None

    print(f"[*] node: {json.dumps(node, ensure_ascii=False)}")
    nid = node["id"]
    hp = node.get("hp_total", 5)
    hits_left = node.get("hits_left", hp)
    print(f"[*] hitting {hits_left} times to break it...")
    for i in range(hits_left + 5):
        s, body = hit(token, nid)
        if s >= 400:
            print(f"    hit err: {body}")
            break
        n2 = body.get("node", {})
        hl = n2.get("hits_left", "?")
        print(f"    hit -> hits_left={hl}")
        if hl == 0:
            break
        time.sleep(0.3)

    s, body = open_node(token, nid)
    print(f"[*] open response status={s} body={json.dumps(body, ensure_ascii=False)}")
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="recon-peakmood-001")
    ap.add_argument("--mode", default="walk", choices=["walk", "stay", "everest", "kilim", "flight", "kpop"])
    ap.add_argument("--rounds", type=int, default=3)
    args = ap.parse_args()

    token, tag = open_session(device_id=args.device)
    print(f"[+] session_token={token} tag={tag}")

    for r in range(args.rounds):
        print(f"\n=== ROUND {r+1}/{args.rounds} ===")
        if args.mode == "walk":
            harvest_one(token, 55.7600 + r * 0.001, 37.6230 + r * 0.001, 180.0, f"Moscow walk #{r+1}")
        elif args.mode == "stay":
            harvest_one(token, 55.7600, 37.6230, 180.0, "Moscow stay")
        elif args.mode == "everest":
            harvest_one(token, 27.9881, 86.925, 8849.0, "Everest")
        elif args.mode == "kilim":
            harvest_one(token, -3.0674, 37.3556, 5895.0, "Kilimanjaro")
        elif args.mode == "flight":
            # try moving across many anchors
            cities = [
                (55.7558, 37.6176, 180, "Moscow"),
                (45.8326, 6.8652, 4808, "Mont Blanc"),
                (27.9881, 86.925, 8849, "Everest"),
            ]
            lat, lon, alt, name = cities[r % 3]
            harvest_one(token, lat, lon, float(alt), name)


if __name__ == "__main__":
    main()
