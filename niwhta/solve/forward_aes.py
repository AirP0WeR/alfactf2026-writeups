#!/usr/bin/env python3
"""Forward AES using the T-tables/S-boxes baked into peace.v.

Mirror of pokoy/solve.py decrypt_internal_block, but going PT -> CT.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POKOY = ROOT / "pokoy" / "solve"
sys.path.insert(0, str(POKOY))

from solve import (  # noqa: E402
    AES_SBOX,
    INV_SBOX,
    INPUT_POS,
    OUTPUT_POS,
    Q_OF_P,
    QIN_OF_P,
    P_BY_COL,
    ROUND_INFO,
    FINAL_INFO,
    build_aes_ttables,
    gmul,
    decrypt_internal_block,
)


AES_TTABLES = build_aes_ttables()


def encrypt_internal_block(pt_internal: bytes) -> bytes:
    """Forward of decrypt_internal_block."""
    state = list(pt_internal)
    for round_idx in range(9):
        nxt = [0] * 16
        for col in range(4):
            word = 0
            for p in P_BY_COL[col]:
                tb, key_in, mask = ROUND_INFO[round_idx * 16 + p]
                x = state[QIN_OF_P[p]] ^ key_in
                word ^= AES_TTABLES[tb][x] ^ mask
            nxt[col * 4 + 0] = (word >> 24) & 0xFF
            nxt[col * 4 + 1] = (word >> 16) & 0xFF
            nxt[col * 4 + 2] = (word >> 8) & 0xFF
            nxt[col * 4 + 3] = word & 0xFF
        state = nxt

    ct = [0] * 16
    for p in range(16):
        key_in, key_out = FINAL_INFO[p]
        ct[Q_OF_P[p]] = AES_SBOX[state[QIN_OF_P[p]] ^ key_in] ^ key_out
    return bytes(ct)


def encrypt_typed_block(typed_block: bytes) -> bytes:
    """Mirror of solve_display_block: typed PT -> 16-byte display CT."""
    canonical_pt = bytes(typed_block[::-1])
    ct_internal = encrypt_internal_block(canonical_pt)
    return ct_internal[::-1]


def selftest_zero() -> None:
    typed = b"\x00" * 16
    display_block = encrypt_typed_block(typed)
    print("AES(zero block) display_hex =", display_block.hex())


def selftest_pokoy() -> None:
    pokoy_flag = b"alfa{whitebox_means_open_floor_plan_3f16ce7b86f56a86f645c24e4b1}"
    expected_hex = (
        "7180dd086c43376b3ca8e2686d0a979b"
        "f823b9666ab992d3cdad80cfe85aed1f"
        "c5c46c60c0a3a5c911a1d198f1835395"
        "53e4b97c165fc43ba3f51e12531feaca"
    )
    actual_blocks = []
    for i in range(0, 64, 16):
        actual_blocks.append(encrypt_typed_block(pokoy_flag[i:i + 16]).hex())
    actual = "".join(actual_blocks)
    print("expected:", expected_hex)
    print("actual:  ", actual)
    print("MATCH" if actual == expected_hex else "MISMATCH")

    # Also round-trip via decrypt to confirm correctness of forward function.
    for i in range(0, 64, 16):
        ct = encrypt_typed_block(pokoy_flag[i:i + 16])
        # decrypt expects display_block; emulate solve_display_block.
        recovered = decrypt_internal_block(ct[::-1])[::-1]
        assert recovered == pokoy_flag[i:i + 16], (i, recovered, pokoy_flag[i:i + 16])
    print("round-trip OK")


if __name__ == "__main__":
    selftest_zero()
    selftest_pokoy()
