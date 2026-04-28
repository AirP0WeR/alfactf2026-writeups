#!/usr/bin/env python3
"""Decode each snapshot and print row 0/1, 2/3, 4/5, 6/7 hex."""
import sys
from pathlib import Path

font = {}
for line in (Path(__file__).resolve().parent / "roms" / "M_00162.txt").read_text().splitlines():
    idx, val = line.split("\t")
    font[int(idx)] = int(val, 16)


def cell_from_font(c):
    rows = []
    for r in range(8):
        bits = format(font.get(c * 8 + r, 0), "06b")
        rows.append(bits.replace("0", ".").replace("1", "#") + "..")
    return rows


# Build glyph dictionary
glyph_to_char = {}
for c in range(128):
    bmp = tuple(cell_from_font(c))
    glyph_to_char[bmp] = c


def parse(path):
    sec = None
    secs = {}
    order = []
    for line in Path(path).read_text().splitlines():
        if line.startswith("## "):
            sec = line[3:].strip()
            secs[sec] = []
            order.append(sec)
        elif sec and len(line) == 128:
            secs[sec].append([1 if c == "#" else 0 for c in line])
    return order, secs


def decode_grid(grid):
    rows_text = []
    for cy in range(8):
        line = ""
        for cx in range(16):
            cell = []
            for y in range(8):
                row = grid[cy * 8 + y][cx * 8 : (cx + 1) * 8]
                cell.append("".join("#" if v else "." for v in row))
            fp = tuple(cell)
            c = glyph_to_char.get(fp, ord("?"))
            line += chr(c)
        rows_text.append(line)
    return rows_text


def main():
    order, secs = parse(sys.argv[1])
    # Header
    print(f"{'#':<14} {'r0':<16} {'r1':<16} {'r2':<16} {'r3':<16} {'r4':<16} {'r5':<16} {'r6':<16} {'r7':<16}")
    last = None
    for name in order:
        rows = decode_grid(secs[name])
        cur = tuple(rows)
        # Mark which rows changed
        diff = ""
        if last:
            for i in range(8):
                diff += "*" if rows[i] != last[i] else "."
        else:
            diff = "........"
        print(f"{name:<14} {' '.join(rows)}    {diff}")
        last = cur


if __name__ == "__main__":
    main()
