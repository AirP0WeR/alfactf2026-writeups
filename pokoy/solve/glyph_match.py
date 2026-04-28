#!/usr/bin/env python3
"""Match observed glyphs from a probe output against the font ROM."""
import sys
from pathlib import Path

# load font
font = {}
for line in (Path(__file__).resolve().parent / "roms" / "M_00162.txt").read_text().splitlines():
    idx, val = line.split("\t")
    font[int(idx)] = int(val, 16)

def char_bitmap(c):
    """Return 8-row × 6-col bitmap for char c."""
    return [font.get(c * 8 + r, 0) for r in range(8)]


# Convert a char's font row to the cell layout used in our extraction.
# Cell is 8 cols wide (we extract 8 px at a time). The font is 6 cols.
# We need to figure out alignment — likely chars are placed left-aligned in 8-col cells with 2 cols of padding on the right.

def cell_from_font(c):
    rows = []
    for r in range(8):
        bits = format(font.get(c * 8 + r, 0), "06b")
        # Font is 6 px wide; cell is 8 px wide. Font is placed at cols 0..5; cols 6..7 padding.
        rows.append(bits.replace("0", ".").replace("1", "#") + "..")
    return rows


def parse_probe(path):
    sec = None
    secs = {}
    for line in Path(path).read_text().splitlines():
        if line.startswith("## "):
            sec = line[3:].strip()
            secs[sec] = []
        elif sec and len(line) == 128:
            secs[sec].append([1 if c == "#" else 0 for c in line])
    return secs


def cells(grid):
    for cy in range(8):
        for cx in range(16):
            cell = []
            for y in range(8):
                row = grid[cy * 8 + y][cx * 8 : (cx + 1) * 8]
                cell.append("".join("#" if v else "." for v in row))
            yield cx, cy, cell


def main():
    secs = parse_probe(sys.argv[1])
    section = sys.argv[2] if len(sys.argv) > 2 else "initial"
    grid = secs[section]

    # gather unique glyph fingerprints
    fp_to_id = {}
    fp_count = {}
    for cx, cy, bmp in cells(grid):
        fp = tuple(bmp)
        if fp not in fp_to_id:
            fp_to_id[fp] = len(fp_to_id)
            fp_count[fp] = 0
        fp_count[fp] += 1

    # match each glyph to font chars
    print(f"Section: {section}, {len(fp_to_id)} unique glyphs")
    glyph_to_char = {}
    for fp, gid in fp_to_id.items():
        # try matching with each char in font
        matched = []
        for c in range(128):
            fc = cell_from_font(c)
            if fc == list(fp):
                matched.append(c)
        glyph_to_char[gid] = matched
        print(f"glyph #{gid:2}  ({fp_count[fp]}× occurrences)  → chars: {[(c, chr(c)) for c in matched]}")
        if not matched:
            for r in fp:
                print("    " + r)

    # render layout using identified chars
    print("\nLayout:")
    for cy in range(8):
        line = ""
        for cx in range(16):
            cell = []
            for y in range(8):
                row = grid[cy * 8 + y][cx * 8 : (cx + 1) * 8]
                cell.append("".join("#" if v else "." for v in row))
            fp = tuple(cell)
            gid = fp_to_id[fp]
            chars = glyph_to_char[gid]
            line += chr(chars[0]) if chars else "?"
        print(f"  {line}")


if __name__ == "__main__":
    main()
