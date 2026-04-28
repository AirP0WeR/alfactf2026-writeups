#!/usr/bin/env python3
"""Dump the font in _M_00162: indexed by {char[6:0], scan_row[2:0]}, 6-bit pixel rows."""
from pathlib import Path

font = {}
for line in (Path(__file__).resolve().parent / "roms" / "M_00162.txt").read_text().splitlines():
    idx, val = line.split("\t")
    font[int(idx)] = int(val, 16)

for ch in range(128):
    rows = []
    for r in range(8):
        rows.append(font.get(ch * 8 + r, 0))
    if all(v == 0 for v in rows):
        continue
    print(f"char {ch:3} (0x{ch:02x}, {chr(ch) if 32<=ch<127 else '?'}):")
    for r in rows:
        bits = format(r, "06b")
        print("  " + bits.replace("0", ".").replace("1", "#"))
    print()
