#!/usr/bin/env python3
<<<<<<< HEAD
"""Probe the design's internal memories via cocotb."""
=======
"""Headless driver for peace.v: feeds a string of keys, returns the framebuffer."""
>>>>>>> 0f878a3 (tasks)
import logging
import os
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


<<<<<<< HEAD
HZ = 1000
HOLD_CYCLES = 110 * HZ // 1000
GAP_CYCLES = 110 * HZ // 1000
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30
INITIAL_SETTLE = 4 + 64 + 30

=======
WIDTH = 128
HEIGHT = 64
>>>>>>> 0f878a3 (tasks)

KEYMAP = {
    "1": 0,  "2": 1,  "3": 2,  "a": 3,  "A": 3,
    "4": 4,  "5": 5,  "6": 6,  "b": 7,  "B": 7,
    "7": 8,  "8": 9,  "9": 10, "c": 11, "C": 11,
    "*": 12, "0": 13, "#": 14, "d": 15, "D": 15,
}

<<<<<<< HEAD
=======
HZ = 1000
HOLD_CYCLES = 110 * HZ // 1000
GAP_CYCLES = 110 * HZ // 1000
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30
INITIAL_SETTLE = 4 + 64 + 30

>>>>>>> 0f878a3 (tasks)

async def step(dut, n=1):
    for _ in range(n):
        dut.clk.value = 0
        await Timer(10, "ns")
        dut.clk.value = 1
        await Timer(11, "ns")


<<<<<<< HEAD
=======
async def scan_display(dut):
    dut.scan_valid.value = 1
    pixels = [[0] * WIDTH for _ in range(HEIGHT)]
    for i in range(HEIGHT):
        dut.scan_row.value = i
        await step(dut)
        bits = dut.scan_pixels.value
        for c, b in enumerate(bits):
            pixels[i][c] = int(b)
    dut.scan_valid.value = 0
    return pixels


>>>>>>> 0f878a3 (tasks)
async def hold_key(dut, key):
    r, c = key // 4, key % 4
    mask = 0xF & ~(1 << c)
    last = 0xF
    for _ in range(HOLD_CYCLES):
        await step(dut)
        rows = int(dut.keypad_rows.value)
        cols = mask if not ((rows >> r) & 1) else 0xF
        if cols != last:
            dut.keypad_cols.value = cols
            last = cols
    if last != 0xF:
        dut.keypad_cols.value = 0xF
    await step(dut, GAP_CYCLES)


<<<<<<< HEAD
def parse_keys(s):
    return [KEYMAP[c] for c in s if c in KEYMAP]


def dump_mem(mem, count, width=8):
    """mem is a cocotb HierarchyArrayObject; return list of int values."""
    out = []
    for i in range(count):
        try:
            v = int(mem[i].value)
        except Exception as e:
            v = -1
        out.append(v)
    return out


@cocotb.test()
async def probe(dut):
    keys_env = os.environ.get("POKOY_KEYS", "")
    keys = parse_keys(keys_env)
=======
def render_lines(pixels):
    out = []
    for y in range(HEIGHT):
        out.append("".join("#" if pixels[y][x] else "." for x in range(WIDTH)))
    return "\n".join(out)


@cocotb.test()
async def peace(dut):
    keys = os.environ.get("PEACE_KEYS", "")
    out_path = os.environ.get("PEACE_OUT", "/tmp/peace_out.txt")
>>>>>>> 0f878a3 (tasks)

    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    await step(dut, INITIAL_SETTLE)

<<<<<<< HEAD
    # Get the named handle for _M_00160_ (input buffer, 64×8)
    # iverilog escaped names — try various
    mem160 = None
    mem162 = None
    for name in ("_M_00160_", "\\_M_00160_ ", "\\_M_00160_"):
        try:
            mem160 = getattr(dut, name)
            sys.stderr.write(f"[probe] found _M_00160_ as {name!r}\n")
            break
        except AttributeError:
            continue
    for name in ("_M_00162_", "\\_M_00162_ ", "\\_M_00162_"):
        try:
            mem162 = getattr(dut, name)
            sys.stderr.write(f"[probe] found _M_00162_ as {name!r}\n")
            break
        except AttributeError:
            continue

    if mem160 is None:
        sys.stderr.write("[probe] dut attrs:\n")
        for n in dir(dut):
            if "M_001" in n or "M_00160" in n or "M_00161" in n or "M_00162" in n:
                sys.stderr.write(f"  {n}\n")

    sys.stderr.write(f"[probe] driving keys {keys_env!r}\n")
    sys.stderr.flush()

    for k in keys:
        await hold_key(dut, k)
        await step(dut, COMMIT_CYCLES)

    if mem160 is not None:
        vals = dump_mem(mem160, 64)
        sys.stdout.write("M160 (input buffer, 64 bytes):\n")
        sys.stdout.write(" ".join(f"{v:02x}" for v in vals) + "\n")

    if mem162 is not None:
        vals = dump_mem(mem162, 1024)
        sys.stdout.write("M162 (framebuffer, 1024×6 bits):\n")
        # print as hex, 16 per line
        for i in range(0, 1024, 16):
            sys.stdout.write(" ".join(f"{v:02x}" for v in vals[i:i+16]) + "\n")

    sys.stdout.flush()
=======
    # Initial scan
    pixels = await scan_display(dut)
    initial = render_lines(pixels)

    # Mode: COMMIT_BETWEEN=1 means press one key, commit, repeat.
    commit_between = os.environ.get("COMMIT_BETWEEN", "0") == "1"
    snapshots = []
    for i, ch in enumerate(keys):
        k = KEYMAP.get(ch)
        if k is None:
            continue
        await hold_key(dut, k)
        if commit_between:
            await step(dut, COMMIT_CYCLES)
            pix = await scan_display(dut)
            snapshots.append((f"{i:02d}_{ch}", render_lines(pix)))

    if not commit_between:
        await step(dut, COMMIT_CYCLES)
    pixels = await scan_display(dut)
    final = render_lines(pixels)

    with open(out_path, "w") as f:
        f.write(f"# keys: {keys!r}\n")
        f.write("## initial\n")
        f.write(initial)
        f.write("\n")
        for ch, snap in snapshots:
            f.write(f"## after {ch!r}\n")
            f.write(snap)
            f.write("\n")
        f.write("## final\n")
        f.write(final)
        f.write("\n")
>>>>>>> 0f878a3 (tasks)


def main():
    os.environ["GPI_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
    os.environ["COCOTB_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
<<<<<<< HEAD
    proj_path = Path("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/pokoy/files/peace_6ce0fda/peace/image/src")
    runner = get_runner("icarus")
    runner.build(
        sources=[proj_path / "peace.v"],
        hdl_toplevel="top",
        timescale=("1ns", "1ps"),
        always=True,
    )
    runner.test(hdl_toplevel="top", test_module="probe", test_dir=Path(__file__).parent)
=======
    src_path = Path(__file__).resolve().parent.parent / "files" / "peace_6ce0fda" / "peace" / "image" / "src"
    runner = get_runner("icarus")
    runner.build(
        sources=[src_path / "peace.v"],
        hdl_toplevel="top",
        timescale=("1ns", "1ps"),
        always=True,
        build_dir=str(Path(__file__).resolve().parent / "sim_build"),
    )
    runner.test(hdl_toplevel="top", test_module="probe", test_dir=str(Path(__file__).resolve().parent))
>>>>>>> 0f878a3 (tasks)


if __name__ == "__main__":
    main()
