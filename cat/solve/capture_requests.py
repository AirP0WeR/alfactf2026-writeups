#!/usr/bin/env python3
"""Open the cat page in headless Chromium, log all network requests + console + DOM."""
from playwright.sync_api import sync_playwright
import os, sys, time, json

OUT = os.path.dirname(os.path.abspath(__file__)) + "/../artifacts"
os.makedirs(OUT, exist_ok=True)

URL = "https://cat-k4sl0sey.alfactf.ru/"

reqs = []
console_logs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()

    page.on("console", lambda m: console_logs.append({"type": m.type, "text": m.text}))
    page.on("request", lambda r: reqs.append({"url": r.url, "method": r.method, "type": r.resource_type}))
    page.on("response", lambda r: print(f"<- {r.status} {r.request.resource_type:10s} {r.url}"))

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # dump final DOM
    html = page.content()
    with open(f"{OUT}/rendered.html", "w") as f:
        f.write(html)

    # dump localStorage / sessionStorage / cookies / window vars
    storage = page.evaluate("""() => ({
      localStorage: Object.fromEntries(Object.entries(localStorage)),
      sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
      cookies: document.cookie,
      title: document.title,
      bodyText: document.body && document.body.innerText,
      hiddenComments: (function(){
         const out = []; const w = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT, null);
         let n; while(n = w.nextNode()) out.push(n.nodeValue);
         return out;
      })(),
      perfEntries: performance.getEntriesByType('resource').map(e => ({name: e.name, type: e.initiatorType, size: e.transferSize})),
    })""")
    with open(f"{OUT}/storage.json","w") as f:
        json.dump(storage, f, indent=2, ensure_ascii=False)

    page.screenshot(path=f"{OUT}/page.png", full_page=True)

    browser.close()

with open(f"{OUT}/requests.json","w") as f:
    json.dump(reqs, f, indent=2)
with open(f"{OUT}/console.json","w") as f:
    json.dump(console_logs, f, indent=2, ensure_ascii=False)

print(f"\n=== {len(reqs)} requests ===")
for r in reqs:
    print(f"{r['method']:6s} {r['type']:10s} {r['url']}")
print(f"\n=== console ({len(console_logs)}) ===")
for c in console_logs:
    print(f"[{c['type']}] {c['text']}")
