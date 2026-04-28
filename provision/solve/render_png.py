#!/usr/bin/env python3
"""Render the 26×80 grid as PNGs (MSB and LSB bit orders, scaled up)."""
from pathlib import Path
import openpyxl

XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"
PASSWORD = "xlmatrix"
ROWS, COLS_BYTES, BITS = 26, 10, 80
SCALE = 14

wb = openpyxl.load_workbook(XLSX, data_only=True)
s3 = wb["s3"]
pad = [[int(s3.cell(row=r, column=c).value) for c in range(4, 14)] for r in range(2, 28)]

ascii_codes = [ord(ch) for ch in PASSWORD]
state = [
    ascii_codes[0] + 256 * ascii_codes[1],
    ascii_codes[2] + 256 * ascii_codes[3],
    ascii_codes[4] + 256 * ascii_codes[5],
    ascii_codes[6] + 256 * ascii_codes[7],
]
MASK = 0xFFFF
out_bytes = []
for n in range(65):
    Bp, Cp, Dp, Ep = state
    F = ((((Bp << 5) ^ (Cp >> 3)) + (Dp ^ (Ep << 1)) + 25713 + n*911) & MASK)
    G = ((((Cp << 4) ^ (Dp >> 2)) + (Ep ^ (Bp << 2)) + 12345 + n*1499) & MASK)
    Bn = (Cp ^ F) & MASK
    Cn = (Dp ^ G) & MASK
    Dn = (Ep ^ ((Bn + 54321 + n*577) & MASK)) & MASK
    En = (Bp ^ ((Cn + 22222 + n*313) & MASK)) & MASK
    out_bytes.extend([Bn & 0xFF, (Cn >> 8) & 0xFF, Dn & 0xFF, (En >> 8) & 0xFF])
    state = [Bn, Cn, Dn, En]

plaintext = [[out_bytes[r*COLS_BYTES + c] ^ pad[r][c] for c in range(COLS_BYTES)] for r in range(ROWS)]


def to_pgm(plain, bit_order, path):
    """Write a scaled binary PGM (no PIL dependency)."""
    grid = [[0]*BITS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS_BYTES):
            byte = plain[r][c]
            for b in range(8):
                bit = (byte >> (7 - b)) & 1 if bit_order == "msb" else (byte >> b) & 1
                grid[r][c*8 + b] = bit
    W, H = BITS * SCALE, ROWS * SCALE
    pixels = bytearray(W * H)
    for r in range(ROWS):
        for c in range(BITS):
            v = 255 if grid[r][c] else 0
            for dy in range(SCALE):
                base = (r*SCALE + dy) * W + c*SCALE
                for dx in range(SCALE):
                    pixels[base + dx] = v
    header = f"P5\n{W} {H}\n255\n".encode()
    Path(path).write_bytes(header + bytes(pixels))


out_dir = Path(__file__).parent
to_pgm(plaintext, "msb", out_dir / "flag_msb.pgm")
to_pgm(plaintext, "lsb", out_dir / "flag_lsb.pgm")
print(f"wrote {out_dir/'flag_msb.pgm'}\nwrote {out_dir/'flag_lsb.pgm'}")
