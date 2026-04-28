#!/usr/bin/env python3
"""Decode the 128x64 framebuffer into 16x8 = 128 hex chars (64 bytes)."""
import sys
from pathlib import Path


def parse(path):
    sections = {}
    cur = None
    cur_name = None
    for line in Path(path).read_text().splitlines():
        if line.startswith("## "):
            if cur_name is not None:
                sections[cur_name] = cur
            cur_name = line[3:].strip()
            cur = []
            continue
        if line.startswith("#"):
            continue
        if cur is not None and len(line) == 128:
            cur.append([1 if c == "#" else 0 for c in line])
    if cur_name is not None:
        sections[cur_name] = cur
    initial = sections.get("initial", [])
    final = sections.get("final", [])
    return initial, final, sections


def cells(grid, cw=8, ch=8):
    """Yield (cx, cy, bitmap rows) for each character cell."""
    rows_n = len(grid) // ch
    cols_n = 128 // cw
    for cy in range(rows_n):
        for cx in range(cols_n):
            cell = []
            for y in range(ch):
                row = grid[cy * ch + y][cx * cw : (cx + 1) * cw]
                cell.append("".join("#" if v else "." for v in row))
            yield cx, cy, cell


def fingerprint(bmp):
    return tuple(bmp)


def gather_glyphs(grids):
    fps = {}
    for g in grids:
        for cx, cy, bmp in cells(g):
            fp = fingerprint(bmp)
            if fp not in fps:
                fps[fp] = len(fps)
    return fps


def grid_to_layout(grid, fps):
    layout = [["?"] * 16 for _ in range(8)]
    for cx, cy, bmp in cells(grid):
        fp = fingerprint(bmp)
        idx = fps[fp]
        if idx < 26:
            layout[cy][cx] = chr(ord('a') + idx)
        else:
            layout[cy][cx] = "?"
    return layout


def main():
    initial, final, sections = parse(sys.argv[1])
    grids = [g for g in sections.values() if g]
    fps = gather_glyphs(grids)
    print(f"unique glyphs across {len(grids)} sections: {len(fps)}")
    for fp, idx in fps.items():
        print(f"\n## glyph #{idx} ({chr(ord('a')+idx) if idx<26 else '?'})")
        for r in fp:
            print(r)
    print()
    for name, g in sections.items():
        if not g:
            continue
        print(f"=== section: {name} ===")
        layout = grid_to_layout(g, fps)
        for row in layout:
            print(" ".join(row))


if __name__ == "__main__":
    main()
