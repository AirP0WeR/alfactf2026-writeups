#!/usr/bin/env python3
"""Offline solver for the niwhta hidden OLED mode.

M_00324_[row] is produced by the same AES core, but with a special plaintext:

    byte 0     = row index 0..3
    byte 1..11 = 0
    byte 12..15 = M_00160[3], M_00160[2], M_00160[1], M_00160[0]

The old notes missed byte 0, so only row 0 matched.  This script searches the
typeable 4-byte prefixes and decodes the OLED bytes in the real, LSB-first
display order.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

SOLVE_DIR = Path(__file__).resolve().parent
ROOT = SOLVE_DIR.parents[1]
POKOY = ROOT / "pokoy" / "solve"
sys.path.insert(0, str(POKOY))

from solve import (  # noqa: E402
    AES_SBOX,
    Q_OF_P,
    QIN_OF_P,
    P_BY_COL,
    ROUND_INFO,
    FINAL_INFO,
    build_aes_ttables,
)

sys.path.insert(0, str(SOLVE_DIR))
from m324_formula import build_mask_for_block  # noqa: E402
from t9 import encode  # noqa: E402


CHARSET = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    " "
    ".,?!"
    "'\":;"
    "-_/\\"
    "@&{}"
    "+"
).encode("ascii")
CHARSET_NP = np.frombuffer(CHARSET, dtype=np.uint8)
BASE = len(CHARSET)
TOTAL = BASE**4

AES_T = [np.array(t, dtype=np.uint32) for t in build_aes_ttables()]
SBOX = np.array(AES_SBOX, dtype=np.uint8)
MASK_BYTES = []
for block_idx in range(4):
    xor_mask, invert_mask = build_mask_for_block(block_idx)
    MASK_BYTES.append(np.frombuffer((xor_mask ^ invert_mask).to_bytes(16, "big"), dtype=np.uint8))


def format_row(row: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in row)


def encrypt_batch(prefixes: np.ndarray, block_idx: int) -> np.ndarray:
    """Return internal AES ciphertexts for a batch of 4-byte prefixes."""
    n = len(prefixes)
    state = np.zeros((n, 16), dtype=np.uint8)
    state[:, 0] = block_idx
    state[:, 12] = prefixes[:, 3]
    state[:, 13] = prefixes[:, 2]
    state[:, 14] = prefixes[:, 1]
    state[:, 15] = prefixes[:, 0]

    for round_idx in range(9):
        nxt = np.empty((n, 16), dtype=np.uint8)
        for col in range(4):
            word = np.zeros(n, dtype=np.uint32)
            for p in P_BY_COL[col]:
                tb, key_in, mask = ROUND_INFO[round_idx * 16 + p]
                idx = np.bitwise_xor(state[:, QIN_OF_P[p]], key_in)
                word ^= AES_T[tb][idx] ^ np.uint32(mask)
            nxt[:, col * 4 + 0] = (word >> np.uint32(24)).astype(np.uint8)
            nxt[:, col * 4 + 1] = (word >> np.uint32(16)).astype(np.uint8)
            nxt[:, col * 4 + 2] = (word >> np.uint32(8)).astype(np.uint8)
            nxt[:, col * 4 + 3] = word.astype(np.uint8)
        state = nxt

    ct = np.empty((n, 16), dtype=np.uint8)
    for p in range(16):
        key_in, key_out = FINAL_INFO[p]
        idx = np.bitwise_xor(state[:, QIN_OF_P[p]], key_in)
        ct[:, Q_OF_P[p]] = np.bitwise_xor(SBOX[idx], key_out)
    return ct


def prefixes_from_range(start: int, stop: int) -> np.ndarray:
    x = np.arange(start, stop, dtype=np.uint64)
    out = np.empty((stop - start, 4), dtype=np.uint8)
    out[:, 0] = CHARSET_NP[((x // (BASE**3)) % BASE).astype(np.intp)]
    out[:, 1] = CHARSET_NP[((x // (BASE**2)) % BASE).astype(np.intp)]
    out[:, 2] = CHARSET_NP[((x // BASE) % BASE).astype(np.intp)]
    out[:, 3] = CHARSET_NP[(x % BASE).astype(np.intp)]
    return out


def decode_display(prefix: bytes) -> list[bytes]:
    rows = []
    p = np.frombuffer(prefix, dtype=np.uint8).reshape(1, 4)
    for block_idx in range(4):
        m324_big = encrypt_batch(p, block_idx)[0] ^ MASK_BYTES[block_idx]
        rows.append(bytes(m324_big[::-1]))
    return rows


def print_candidate(prefix: bytes) -> None:
    rows = decode_display(prefix)
    flag = b"".join(rows)
    print(f"typed first 4 bytes: {prefix!r}")
    print(f"keypad sequence: {encode(prefix.decode('ascii'))}")
    print("OLED rows:")
    for row in rows:
        print(format_row(row))
    print(f"as 64 bytes: {flag!r}")
    if flag.startswith(b"alfa{") and b"}" in flag:
        print("flag:", flag[: flag.index(b'}') + 1].decode("ascii", errors="replace"))
    print()


def search(batch_size: int = 1_000_000) -> list[bytes]:
    hits: list[bytes] = []
    started = time.time()
    for start in range(0, TOTAL, batch_size):
        stop = min(start + batch_size, TOTAL)
        prefixes = prefixes_from_range(start, stop)

        row0 = encrypt_batch(prefixes, 0) ^ MASK_BYTES[0]
        # Real OLED character order is LSB-first, so "alfa{" means big bytes
        # [15], [14], [13], [12], [11].
        m = (
            (row0[:, 15] == ord("a"))
            & (row0[:, 14] == ord("l"))
            & (row0[:, 13] == ord("f"))
            & (row0[:, 12] == ord("a"))
            & (row0[:, 11] == ord("{"))
        )
        if not np.any(m):
            if start and start % (batch_size * 8) == 0:
                rate = stop / max(time.time() - started, 1e-9)
                print(f"checked {stop:,}/{TOTAL:,} ({rate:,.0f}/s)", file=sys.stderr)
            continue

        idxs = np.flatnonzero(m)
        row3 = encrypt_batch(prefixes[idxs], 3) ^ MASK_BYTES[3]
        idxs = idxs[row3[:, 0] == ord("}")]
        for idx in idxs:
            hits.append(bytes(prefixes[idx]))
            print_candidate(hits[-1])

    return hits


def main() -> None:
    if len(sys.argv) > 1:
        print_candidate(sys.argv[1].encode("ascii"))
        return
    hits = search()
    print(f"hits: {len(hits)}")


if __name__ == "__main__":
    main()
