#!/usr/bin/env python3
import json
from pathlib import Path


DATA = json.loads(Path(__file__).with_name("aes_data.json").read_text())
TTABLES = DATA["ttables"]
SBOXES = DATA["sboxes"]

DISPLAY_CT_HEX = (
    "71 80 dd 08 6c 43 37 6b 3c a8 e2 68 6d 0a 97 9b "
    "f8 23 b9 66 6a b9 92 d3 cd ad 80 cf e8 5a ed 1f "
    "c5 c4 6c 60 c0 a3 a5 c9 11 a1 d1 98 f1 83 53 95 "
    "53 e4 b9 7c 16 5f c4 3b a3 f5 1e 12 53 1f ea ca"
)

AES_SBOX = [
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
]

INV_SBOX = [0] * 256
for i, v in enumerate(AES_SBOX):
    INV_SBOX[v] = i

# Table/sbox wiring extracted from peace.v.
INPUT_POS = [15, 14, 5, 4, 3, 2, 1, 0, 13, 12, 11, 10, 9, 8, 7, 6]
OUTPUT_POS = [15, 2, 13, 0, 3, 6, 9, 12, 5, 8, 11, 14, 1, 4, 7, 10]
Q_OF_P = [15 - pos for pos in OUTPUT_POS]
QIN_OF_P = [15 - pos for pos in INPUT_POS]
P_BY_COL = [[], [], [], []]
for p, q in enumerate(Q_OF_P):
    P_BY_COL[q // 4].append(p)


def xtime(b: int) -> int:
    return ((b << 1) ^ (0x1B if b & 0x80 else 0)) & 0xFF


def gmul(a: int, b: int) -> int:
    out = 0
    for _ in range(8):
        if b & 1:
            out ^= a
        a = xtime(a)
        b >>= 1
    return out & 0xFF


def build_aes_ttables() -> list[list[int]]:
    tables = [[0] * 256 for _ in range(4)]
    for x in range(256):
        s = AES_SBOX[x]
        m2 = gmul(s, 2)
        m3 = gmul(s, 3)
        tables[0][x] = (m2 << 24) | (s << 16) | (s << 8) | m3
        tables[1][x] = (m3 << 24) | (m2 << 16) | (s << 8) | s
        tables[2][x] = (s << 24) | (m3 << 16) | (m2 << 8) | s
        tables[3][x] = (s << 24) | (s << 16) | (m3 << 8) | m2
    return tables


def extract_table_info() -> tuple[list[tuple[int, int, int]], list[tuple[int, int]]]:
    aes_ttables = build_aes_ttables()
    round_info: list[tuple[int, int, int]] = []
    for table in TTABLES:
        found = None
        for tb in range(4):
            for key_in in range(256):
                mask = table[0] ^ aes_ttables[tb][key_in]
                if all(table[x] == (aes_ttables[tb][x ^ key_in] ^ mask) for x in range(256)):
                    found = (tb, key_in, mask)
                    break
            if found is not None:
                break
        if found is None:
            raise RuntimeError("failed to classify T-table")
        round_info.append(found)

    final_info: list[tuple[int, int]] = []
    for sbox in SBOXES:
        found = None
        for key_in in range(256):
            key_out = sbox[0] ^ AES_SBOX[key_in]
            if all(sbox[x] == (AES_SBOX[x ^ key_in] ^ key_out) for x in range(256)):
                found = (key_in, key_out)
                break
        if found is None:
            raise RuntimeError("failed to classify final S-box")
        final_info.append(found)

    return round_info, final_info


ROUND_INFO, FINAL_INFO = extract_table_info()


def inv_mix_column(col: list[int]) -> list[int]:
    return [
        gmul(col[0], 0x0E) ^ gmul(col[1], 0x0B) ^ gmul(col[2], 0x0D) ^ gmul(col[3], 0x09),
        gmul(col[0], 0x09) ^ gmul(col[1], 0x0E) ^ gmul(col[2], 0x0B) ^ gmul(col[3], 0x0D),
        gmul(col[0], 0x0D) ^ gmul(col[1], 0x09) ^ gmul(col[2], 0x0E) ^ gmul(col[3], 0x0B),
        gmul(col[0], 0x0B) ^ gmul(col[1], 0x0D) ^ gmul(col[2], 0x09) ^ gmul(col[3], 0x0E),
    ]


def decrypt_internal_block(ct_internal: bytes) -> bytes:
    state = [0] * 16

    for p, q in enumerate(Q_OF_P):
        key_in, key_out = FINAL_INFO[p]
        state[QIN_OF_P[p]] = INV_SBOX[ct_internal[q] ^ key_out] ^ key_in

    for round_idx in range(8, -1, -1):
        prev = [0] * 16
        for col in range(4):
            col_bytes = state[col * 4 : col * 4 + 4]
            mask_total = 0
            for p in P_BY_COL[col]:
                mask_total ^= ROUND_INFO[round_idx * 16 + p][2]
            clean = ((col_bytes[0] << 24) | (col_bytes[1] << 16) | (col_bytes[2] << 8) | col_bytes[3]) ^ mask_total
            sbox_out = inv_mix_column(
                [(clean >> 24) & 0xFF, (clean >> 16) & 0xFF, (clean >> 8) & 0xFF, clean & 0xFF]
            )
            for p in P_BY_COL[col]:
                tb, key_in, _ = ROUND_INFO[round_idx * 16 + p]
                prev[QIN_OF_P[p]] = INV_SBOX[sbox_out[tb]] ^ key_in
        state = prev

    return bytes(state)


def solve_display_block(display_block: bytes) -> bytes:
    # The OLED prints M325 bytes in reverse order within each 128-bit block.
    internal = display_block[::-1]
    canonical_pt = decrypt_internal_block(internal)
    # The typed buffer uses the reverse byte order of the canonical AES block.
    return canonical_pt[::-1]


def main() -> None:
    display_ct = bytes.fromhex(DISPLAY_CT_HEX)
    blocks = [display_ct[i : i + 16] for i in range(0, len(display_ct), 16)]
    plaintext = b"".join(solve_display_block(block) for block in blocks)
    print(plaintext.decode("ascii"))


if __name__ == "__main__":
    main()
