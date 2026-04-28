#!/usr/bin/env python3
"""Parse the framebuffer dumps from drive.py into the displayed 64-byte hex matrix.

Display layout (from inspection of empty input):
  - 128x64 framebuffer
  - 8 text rows of 16 hex digits each (each glyph 8x8 pixels)
  - Row pixel range: y in [r*8, r*8+8); col pixel range: x in [c*8, c*8+8)

Glyphs are 6 wide / 7 high inside an 8x8 cell — we'll classify by
matching against known empty-input pattern OR by template-matching.
"""
import sys
from pathlib import Path

GLYPH_W = 8
GLYPH_H = 8


def load_dump(path):
    """Returns (pre_pixels, post_pixels) as lists of 64-row × 128-col lists of 0/1."""
    text = Path(path).read_text().splitlines()
    pre = []
    post = []
    cur = None
    for line in text:
        if line == "PRE:":
            cur = pre
            continue
        if line == "POST:":
            cur = post
            continue
        if line.startswith("keys="):
            continue
        if cur is None:
            continue
        if not line:
            continue
        # parse 0/1 line
        row = [1 if c == '#' else 0 for c in line[:128]]
        if len(row) < 128:
            row += [0]*(128-len(row))
        cur.append(row)
    return pre[:64], post[:64]


def extract_glyphs(pixels):
    """Return list of 64 (8x8) glyphs as tuples of bits, in row-major (top-left to bot-right)."""
    glyphs = []
    for r in range(8):
        for c in range(16):
            bits = []
            for dy in range(GLYPH_H):
                for dx in range(GLYPH_W):
                    bits.append(pixels[r*8+dy][c*8+dx])
            glyphs.append(tuple(bits))
    return glyphs


def build_templates(pre_glyphs):
    """In an empty (zero) framebuffer the displayed digits form the canonical template:
    each glyph in row 0..7 col 0..15 has known content -- but we don't know it yet.
    Instead, since the empty display visually looks like 16 unique hex chars repeated,
    we'll try assuming text 'alfa{...}' isn't there. We need ground truth.

    Strategy: pre_glyphs has 128 glyphs. For all-zero data the M_00160 buffer is all
    0x00 → all 128 hex digits are '0'. But we visually saw varying glyphs!
    So the M_00160 buffer is NOT what's displayed directly. Display content is
    derived (e.g., displayed = encrypt(M_00160) or shows a fixed pattern).

    Just dump unique glyphs.
    """
    uniq = {}
    for g in pre_glyphs:
        uniq.setdefault(g, 0)
        uniq[g] += 1
    return uniq


def render_glyph(g):
    """Pretty-print 8x8 glyph."""
    out = []
    for y in range(8):
        out.append("".join("#" if g[y*8+x] else "." for x in range(8)))
    return "\n".join(out)


def main():
    pre, post = load_dump(sys.argv[1])
    pre_g = extract_glyphs(pre)
    post_g = extract_glyphs(post)
    print(f"PRE  glyphs={len(pre_g)} unique={len(set(pre_g))}")
    print(f"POST glyphs={len(post_g)} unique={len(set(post_g))}")
    print(f"diff cells: {sum(1 for a,b in zip(pre_g,post_g) if a!=b)}")

    uniq = list({*pre_g, *post_g})
    cls = {g: i for i, g in enumerate(uniq)}
    print("PRE grid:")
    for r in range(8):
        print(" ".join(f"{cls[pre_g[r*16+c]]:3d}" for c in range(16)))
    print("POST grid:")
    for r in range(8):
        print(" ".join(f"{cls[post_g[r*16+c]]:3d}" for c in range(16)))
    if "--render" in sys.argv:
        for i, g in enumerate(uniq):
            print(f"--- glyph #{i} (pre={pre_g.count(g)}, post={post_g.count(g)})")
            print(render_glyph(g))


if __name__ == "__main__":
    main()
