#!/usr/bin/env python3
"""Extract S-boxes and T-tables from peace.v as binary blobs."""
import re
import json
from pathlib import Path

V = Path("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/pokoy/files/peace_6ce0fda/peace/image/src/peace.v").read_text()


def extract_8bit(name):
    """Extract memory `name` initial values as list of 256 ints."""
    rx = re.compile(rf"\\{name} \[(\d+)\] = 8'h([0-9a-f]+);")
    out = [0] * 256
    for m in rx.finditer(V):
        i = int(m.group(1))
        v = int(m.group(2), 16)
        out[i] = v
    return out


def extract_32bit(name):
    """Extract 32-bit memory."""
    rx = re.compile(rf"\\{name} \[(\d+)\] = 32'd(\d+);")
    out = [0] * 256
    for m in rx.finditer(V):
        i = int(m.group(1))
        v = int(m.group(2))
        out[i] = v
    return out


def all_sboxes():
    """Final-round 8-bit S-boxes _M_00000 ... _M_00015"""
    return [extract_8bit(f"_M_{i:05d}_") for i in range(16)]


def all_ttables():
    """T-tables _M_00016 ... _M_00159 (144 tables, 32-bit values)."""
    return [extract_32bit(f"_M_{i:05d}_") for i in range(16, 160)]


if __name__ == "__main__":
    sboxes = all_sboxes()
    ttables = all_ttables()
    print(f"Got {len(sboxes)} sboxes, {len(ttables)} ttables")
    print(f"sbox0[:8] = {sboxes[0][:8]}")
    print(f"ttable0[:4] = {ttables[0][:4]}")

    # check sboxes are permutations
    for i, s in enumerate(sboxes):
        assert len(set(s)) == 256, f"sbox {i} not a perm"
    print("All 16 final-round sboxes are permutations.")

    # save as json
    out = {
        "sboxes": sboxes,
        "ttables": ttables,
    }
    Path("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/pokoy/solve/aes_data.json").write_text(json.dumps(out))
    print("saved to aes_data.json")
