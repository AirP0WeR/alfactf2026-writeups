#!/usr/bin/env python3
"""
probe40: small-list ffuf-like brute on / using common paths.
"""
import json
import ssl
import time
import urllib.request
import urllib.error
import hashlib

HOST = "funicular-gm2cxozn.alfactf.ru"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

WORDS = """
about access account action actions admin administrator advanced ajax alert all api
app application apps archive assets attach attachment audit auth authenticate
authorize backup backups beta blog bin board bot build cache calendar callback cdn
chat check checks ci client clients cloud cluster code commit commits common config
configuration console contact content control controller cookie core cron css
customer dashboard data db debug default delete deploy deployment design dev devel
development device diagnostic diagnostics dispatch dist doc docs documentation
download downloads e2e edit editor email engineer error errors exec export
external faq favicon feature features feed feedback file files filter
finance form forms forum gateway git github graph graphql group groups guest
guide hash health help hidden home host hosting hot html http https
icon icons idle image images img import index info insert install
internal intern intl invite invoice issue issues item items join js json key keys lan
language ldap lib library license link list load loader local locale log login
logout logs main maintenance manage manager map maps me media member mfa
migrate migration mock mode module modules monitor monitoring mount move my mysql
namespace native net network new news note notes notification notify oauth offline
old open operator option options order orders organization out output
package packages page pages parent parse partner password path payment payments
performance permission permissions phpinfo phpmyadmin ping plan plc plugin pool port
post postman pre preview private prod production profile project projects prom
properties protected provider proxy public pubsub push python qa query queue
quota raw rc react read reactjs reboot recipe record records recover recovery
redirect redis register registration regulator regulatory release remote remove
render report reports request requests reset resource resources response rest
restart restore retrieve revoke role roles room route routes ruby run runtime
sample save saved schedule schema script search secret secrets section secure
security send sensor server service services session settings setup shared
shell show shutdown sign signal signin signout signup site sites sitemap slack
sms snapshot snapshots socket source spec ssh ssl stack staff stage staging
start state stat static stats status stop storage store stream string sub subscribe
subscription subscriptions super support sync system table tag tags task tasks
team teams telegram telemetry temp template templates tenant test testing
text the theme third token tokens tool tools track trade trace trailer
transaction transactions tree trial tx type ui uninstall update updater upgrade
upload uploads url use user users util utils v1 v2 v3 valid validate value
vault vendor verification verify version vfs view views vm vue web webapp webhook
websocket whoami widget wiki window wp wp-admin wp-login www xml yaml zip zone
""".split()

found = []

def get(path):
    url = f"https://{HOST}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "p40"}, method="GET")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=10) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        return e.code, dict(e.headers), data
    except Exception as e:
        return -1, {}, str(e).encode()


# Get baselines first
st_404, _, body_404 = get("/__definitely_not_exists_12345")
sha_404 = hashlib.sha256(body_404).hexdigest()[:16]
print(f"# baseline 404 sha={sha_404} st={st_404} len={len(body_404)}")

print("\n# Brute /WORD")
for w in WORDS:
    p = f"/{w}"
    st, h, body = get(p)
    sha = hashlib.sha256(body).hexdigest()[:16]
    if st not in (404,) or sha != sha_404:
        ct = h.get("Content-Type", "")
        cache = h.get("X-Nextjs-Cache", "")
        print(f"  {p:30s} st={st} len={len(body)} sha={sha} cache={cache} ct={ct[:40]}")
        found.append((p, st, len(body)))
    time.sleep(0.05)

print(f"\n# Brute /admin/WORD (cache HIT for /admin)")
st_404a, _, body_404a = get("/admin/__nope__123")
sha_404a = hashlib.sha256(body_404a).hexdigest()[:16]
print(f"# baseline /admin/404 sha={sha_404a} st={st_404a}")
for w in WORDS[:80]:
    p = f"/admin/{w}"
    st, h, body = get(p)
    sha = hashlib.sha256(body).hexdigest()[:16]
    if st not in (404,) or sha != sha_404a:
        print(f"  {p:30s} st={st} len={len(body)} sha={sha}")
        found.append((p, st, len(body)))
    time.sleep(0.05)

print(f"\n# Brute /api/operator/WORD")
st_404b, _, body_404b = get("/api/operator/__nope__123")
sha_404b = hashlib.sha256(body_404b).hexdigest()[:16]
print(f"# baseline /api/operator/404 sha={sha_404b} st={st_404b}")
for w in WORDS:
    p = f"/api/operator/{w}"
    st, h, body = get(p)
    sha = hashlib.sha256(body).hexdigest()[:16]
    if st not in (404,) or sha != sha_404b:
        print(f"  {p:30s} st={st} len={len(body)} sha={sha}")
        found.append((p, st, len(body)))
    time.sleep(0.05)

print(f"\n# Brute /api/WORD")
st_404c, _, body_404c = get("/api/__nope__123")
sha_404c = hashlib.sha256(body_404c).hexdigest()[:16]
print(f"# baseline /api/404 sha={sha_404c} st={st_404c}")
for w in WORDS:
    p = f"/api/{w}"
    st, h, body = get(p)
    sha = hashlib.sha256(body).hexdigest()[:16]
    if st not in (404,) or sha != sha_404c:
        print(f"  {p:30s} st={st} len={len(body)} sha={sha}")
        found.append((p, st, len(body)))
    time.sleep(0.05)

print(f"\n# All hits: {len(found)}")
for f in found:
    print(f"  {f}")

print("\n# done.")
