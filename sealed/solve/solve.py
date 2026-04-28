#!/usr/bin/env python3
"""DeviceVault sync_state.dat decryption — Alfa CTF 2026 / sealed.

Usage:
    SEALED_DUMP=/path/to/extracted/dump python3 solve.py [--fetch]

The dump root must contain `private/var/mobile/Containers/Data/Application/
03E00EEB-FFCA-401D-9607-656B163BD6E7/{Documents/sync_state.dat,
Library/Caches/com.apple.sync.device}`.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


CONTAINER = "03E00EEB-FFCA-401D-9607-656B163BD6E7"

UDID = "818f51114fe9694e93b02e8ddb3534e3e71d9ec0"
SERIAL = "C8PWL460JWF7"
ECID = "000C28403808E02E"
IMEI = "352989095784185"

WIFI = "647033b23730"          # MGCopyAnswer("WifiAddress") → lowercased, colons stripped
BLUETOOTH = "64:70:33:B2:70:DC"  # MGCopyAnswer("BluetoothAddress") → uppercased, colons kept
ICCID = "8997103124066584148"

WEATHER_CONTAINER = "2E3D73AC-3BBE-476A-9CFF-70D323D9ED27"  # com.apple.weather data UUID
BUNDLE_ID = "com.devicevault.app"
VAULT_SUFFIX = ".v1"      # config.plist
SCHEMA_VERSION = 10007    # config.plist (PBKDF2 iterations)


def derive_key(secret: bytes) -> bytes:
    if len(secret) != 32:
        raise ValueError(f"unexpected keychain cache length: {len(secret)}")

    hw_hash = hashlib.sha256((UDID + SERIAL + ECID + IMEI).encode()).digest()
    network = (WIFI + BLUETOOTH + ICCID).encode()

    # The Swift PBKDF2 wrapper (sym.func.1000077c4) takes (data1, data2) and
    # passes data1 as `password`, data2 as `salt`. Master delivers the
    # HMAC-SHA256 result as data1, the SHA256 result as data2 — so:
    pbkdf_password = hmac.new(hw_hash, network, hashlib.sha256).digest()
    pbkdf_salt = hashlib.sha256(secret + WEATHER_CONTAINER.encode()).digest()
    pbkdf = hashlib.pbkdf2_hmac(
        "sha256", pbkdf_password, pbkdf_salt, SCHEMA_VERSION, 32
    )

    # HKDF-Expand with info = "com.devicevault.app" + ".v1", L=32 → 1 block
    info = (BUNDLE_ID + VAULT_SUFFIX).encode()
    return hmac.new(pbkdf, info + b"\x01", hashlib.sha256).digest()


def decrypt_state(dump_root: Path) -> dict:
    app = dump_root / f"private/var/mobile/Containers/Data/Application/{CONTAINER}"
    secret = (app / "Library/Caches/com.apple.sync.device").read_bytes()
    blob = (app / "Documents/sync_state.dat").read_bytes()
    nonce, ct_tag = blob[:12], blob[12:]
    plain = AESGCM(derive_key(secret)).decrypt(nonce, ct_tag, None)
    return json.loads(plain)


def fetch_flag(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    match = re.search(r"alfa\{[^}]+\}", html)
    if not match:
        raise ValueError("flag not found in drop response")
    return match.group(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Decrypt DeviceVault sync_state.dat")
    parser.add_argument(
        "--dump",
        default=os.environ.get("SEALED_DUMP", "."),
        help="path to extracted SEALED_DUMP root (or set SEALED_DUMP env var)",
    )
    parser.add_argument("--fetch", action="store_true", help="GET the drop URL")
    args = parser.parse_args()

    dump_root = Path(args.dump).expanduser().resolve()
    if not (dump_root / "private/var/mobile/Containers").is_dir():
        print(
            f"[!] {dump_root} does not look like a SEALED_DUMP root. "
            "Pass --dump or set SEALED_DUMP env var.",
            file=sys.stderr,
        )
        sys.exit(2)

    state = decrypt_state(dump_root)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    drop_url = state["entries"][0]["secret"]
    print(f"\ndrop_url = {drop_url}")

    if args.fetch:
        print(f"flag     = {fetch_flag(drop_url)}")


if __name__ == "__main__":
    main()
