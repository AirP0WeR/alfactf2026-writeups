#!/usr/bin/env python3
"""Decode 128x64 pixel grid to hex string assuming 8x8 hex-digit glyphs."""

# 8x8 hex digit font we'll learn empirically. We'll print each glyph, dedupe.

def parse_pixels(text):
    """Parse FINAL_DISPLAY block into 128x64 pixel array."""
    lines = text.strip().split("\n")
    BLOCKS_INV = {
        " ": 0b0000, "▗": 0b0001, "▖": 0b0010, "▄": 0b0011,
        "▝": 0b0100, "▐": 0b0101, "▞": 0b0110, "▟": 0b0111,
        "▘": 0b1000, "▚": 0b1001, "▌": 0b1010, "▙": 0b1011,
        "▀": 0b1100, "▜": 0b1101, "▛": 0b1110, "█": 0b1111,
    }
    pixels = [[0] * 128 for _ in range(64)]
    for gy, line in enumerate(lines):
        # ensure line is right length
        line = line + " " * (64 - len(line))
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


def show_glyph(pixels, gx, gy, w=8, h=8):
    """gx,gy in glyph coords; print 8x8 block."""
    out = []
    for r in range(h):
        row = ""
        for c in range(w):
            row += "#" if pixels[gy * h + r][gx * w + c] else "."
        out.append(row)
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    text = sys.stdin.read()
    # find FINAL_DISPLAY: section
    if "FINAL_DISPLAY:" in text:
        text = text.split("FINAL_DISPLAY:", 1)[1]
    # take first 32 non-empty lines
    lines = [ln for ln in text.split("\n") if ln.strip() != ""][:32]
    pixels = parse_pixels("\n".join(lines))

    # Try 16 cols × 8 rows of 8x8 glyphs → 128 hex digits = 64 bytes
    print("Glyphs as 16 cols × 8 rows:")
    for gy in range(8):
        for gx in range(16):
            print(f"=== glyph ({gx},{gy}) ===")
            print(show_glyph(pixels, gx, gy))
        print()
