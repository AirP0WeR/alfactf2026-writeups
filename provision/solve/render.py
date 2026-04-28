#!/usr/bin/env python3
"""
Replay the s2 PRG + s3 XOR-with-pad → render the 26×80 bit grid for password
'xlmatrix'. Read the flag visually from the output.
"""

import openpyxl
from pathlib import Path

XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"
PASSWORD = "xlmatrix"
ROWS = 26
COLS_BYTES = 10  # → 80 bits per row

assert len(PASSWORD) == 8

wb = openpyxl.load_workbook(XLSX, data_only=True)
s3 = wb["s3"]

# 26x10 constant XOR pad from s3!D2:M27.
pad = []
for r in range(2, 28):           # rows 2..27 inclusive
    row = []
    for c in range(4, 14):       # columns D=4 .. M=13 inclusive
        row.append(int(s3.cell(row=r, column=c).value))
    pad.append(row)
assert len(pad) == ROWS and all(len(r) == COLS_BYTES for r in pad)


# Replay s2 PRG.
ascii_codes = [ord(ch) for ch in PASSWORD]
B2, C2, D2, E2, F2, G2, H2, I2 = ascii_codes  # s2!B2..I2

# s2!B4:E4 — pack pairs into 16-bit words, low byte first.
state = [
    B2 + 256 * C2,   # B4
    D2 + 256 * E2,   # C4
    F2 + 256 * G2,   # D4
    H2 + 256 * I2,   # E4
]

MASK = 0xFFFF
out_bytes = []  # 4 bytes per iteration (H,I,J,K)

for n in range(65):  # rows 6..70 inclusive → A6=0 ... A70=64
    Bp, Cp, Dp, Ep = state
    F = ((((Bp << 5) ^ (Cp >> 3)) + (Dp ^ (Ep << 1)) + 25713 + n * 911) & MASK)
    G = ((((Cp << 4) ^ (Dp >> 2)) + (Ep ^ (Bp << 2)) + 12345 + n * 1499) & MASK)
    Bn = (Cp ^ F) & MASK
    Cn = (Dp ^ G) & MASK
    Dn = (Ep ^ ((Bn + 54321 + n * 577) & MASK)) & MASK
    En = (Bp ^ ((Cn + 22222 + n * 313) & MASK)) & MASK
    H = Bn & 0xFF                  # s2!H{r}
    I = (Cn >> 8) & 0xFF           # s2!I{r}
    J = Dn & 0xFF                  # s2!J{r}
    K = (En >> 8) & 0xFF           # s2!K{r}
    out_bytes.extend([H, I, J, K])
    state = [Bn, Cn, Dn, En]

assert len(out_bytes) == 260

# XOR with the pad.
plaintext = []
for r in range(ROWS):
    row_p = []
    for c in range(COLS_BYTES):
        idx = r * COLS_BYTES + c
        row_p.append(out_bytes[idx] ^ pad[r][c])
    plaintext.append(row_p)


def render(bit_order: str):
    print(f"\n=== bit order: {bit_order} ===")
    for r in range(ROWS):
        line = []
        for c in range(COLS_BYTES):
            byte = plaintext[r][c]
            if bit_order == "msb":
                bits = [(byte >> (7 - b)) & 1 for b in range(8)]
            else:
                bits = [(byte >> b) & 1 for b in range(8)]
            for bit in bits:
                line.append("█" if bit else "·")
        print("".join(line))


render("msb")
render("lsb")

# Also dump the raw plaintext bytes for manual inspection.
out_path = Path(__file__).parent / "plaintext.bin"
out_path.write_bytes(bytes(b for row in plaintext for b in row))
print(f"\nplaintext bytes written to {out_path}")
