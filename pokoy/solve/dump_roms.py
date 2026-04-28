#!/usr/bin/env python3
"""Extract all _M_xxxxx_ memory init values from peace.v."""
import re
import sys
from pathlib import Path
from collections import defaultdict


def main(path):
    src = Path(path).read_text()
    pat = re.compile(r"\\_M_(\d{5})_\s*\[(\d+)\]\s*=\s*(\d+)'h([0-9a-fA-F]+)\s*;")
    roms = defaultdict(dict)
    bits = {}
    for m in pat.finditer(src):
        rom = int(m.group(1))
        idx = int(m.group(2))
        nbits = int(m.group(3))
        val = int(m.group(4), 16)
        roms[rom][idx] = val
        bits[rom] = nbits
    return roms, bits


def maybe_perm(d):
    vals = list(d.values())
    return len(set(vals)) == len(vals) and len(vals) == 256 and set(vals) == set(range(256))


if __name__ == "__main__":
    roms, bits = main(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(exist_ok=True)
    for rom_id in sorted(roms.keys()):
        d = roms[rom_id]
        nbits = bits[rom_id]
        sz = len(d)
        is_perm = maybe_perm(d) if nbits == 8 else False
        first = " ".join(f"{d[i]:02x}" for i in range(min(8, sz)) if i in d) if nbits <= 8 else ""
        print(f"M_{rom_id:05d}: {nbits} bits, {sz} entries, perm={is_perm}  first={first}")
        # save dump
        with open(out_dir / f"M_{rom_id:05d}.txt", "w") as f:
            for i in sorted(d):
                f.write(f"{i}\t{d[i]:0{(nbits+3)//4}x}\n")
