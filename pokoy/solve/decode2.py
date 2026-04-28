#!/usr/bin/env python3
"""Decode 128x64 pixel grid: collect unique glyphs, see how many."""
import sys

BLOCKS_INV = {
    " ": 0b0000, "▗": 0b0001, "▖": 0b0010, "▄": 0b0011,
    "▝": 0b0100, "▐": 0b0101, "▞": 0b0110, "▟": 0b0111,
    "▘": 0b1000, "▚": 0b1001, "▌": 0b1010, "▙": 0b1011,
    "▀": 0b1100, "▜": 0b1101, "▛": 0b1110, "█": 0b1111,
}


def parse_pixels(text):
    """text: 32 lines of 64 quadrant-glyph chars each."""
    lines = [ln + " " * 64 for ln in text.split("\n")][:32]
    pixels = [[0] * 128 for _ in range(64)]
    for gy in range(32):
        line = lines[gy]
        for gx in range(64):
            ch = line[gx] if gx < len(line) else " "
            v = BLOCKS_INV.get(ch, 0)
            y = gy * 2
            x = gx * 2
            pixels[y][x] = (v >> 3) & 1
            pixels[y][x + 1] = (v >> 2) & 1
            pixels[y + 1][x] = (v >> 1) & 1
            pixels[y + 1][x + 1] = v & 1
    return pixels


def glyph(pixels, gx, gy, w=8, h=8):
    s = ""
    for r in range(h):
        for c in range(w):
            s += "#" if pixels[gy * h + r][gx * w + c] else "."
        s += "\n"
    return s


if __name__ == "__main__":
    text = sys.stdin.read()
    if "FINAL_DISPLAY:" in text:
        text = text.split("FINAL_DISPLAY:", 1)[1]
    text = text.lstrip("\n")
    pixels = parse_pixels(text)

    # Try various grid sizes
    for w, h, label in [(8, 8, "8x8"), (8, 16, "8x16"), (16, 8, "16x8"), (8, 4, "8x4")]:
        cols = 128 // w
        rows = 64 // h
        glyphs = {}
        for gy in range(rows):
            for gx in range(cols):
                g = glyph(pixels, gx, gy, w, h)
                glyphs.setdefault(g, []).append((gx, gy))
        print(f"=== layout {label}: {cols}x{rows} cells, unique={len(glyphs)} ===")
        if len(glyphs) <= 30:
            # tag with sequential ids
            id_map = {g: i for i, g in enumerate(sorted(glyphs.keys(), key=lambda g: glyphs[g][0]))}
            grid = [["?"] * cols for _ in range(rows)]
            for g, locs in glyphs.items():
                for gx, gy in locs:
                    grid[gy][gx] = format(id_map[g], "x") if id_map[g] < 16 else "Z"
            for row in grid:
                print("  " + "".join(row))
            # print glyph art for each unique
            for g, gid in sorted(id_map.items(), key=lambda kv: kv[1]):
                print(f"  -- id {gid:x} at {glyphs[g][:3]}:")
                for line in g.rstrip("\n").split("\n"):
                    print("    " + line)
        print()
