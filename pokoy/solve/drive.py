#!/usr/bin/env python3
"""Non-interactive cocotb driver for peace.v.

Reads keypad sequence from $POKOY_KEYS, drives the simulated keypad,
commits, scans the framebuffer, and writes:
  - $POKOY_OUT_FB   binary 8192-bit (=1024-byte) framebuffer (row-major, 64x128)
  - $POKOY_OUT_HEX  64-byte hex matrix that's expected to match displayed digits
                    (the "diagnostics" interpretation: bottom 64 bytes of M_00160)
We don't actually know the exact display layout for the digit grid, so we just
dump pixels and hex matrix; caller can post-process.
"""
import logging
import os
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


WIDTH = 128
HEIGHT = 64

KEYMAP = {
    "1": 0,  "2": 1,  "3": 2,  "a": 3,  "A": 3,
    "4": 4,  "5": 5,  "6": 6,  "b": 7,  "B": 7,
    "7": 8,  "8": 9,  "9": 10, "c": 11, "C": 11,
    "*": 12, "0": 13, "#": 14, "d": 15, "D": 15,
}

HZ = 1000
HOLD_CYCLES = 110 * HZ // 1000
GAP_CYCLES = 110 * HZ // 1000
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30
INITIAL_SETTLE = 4 + 64 + 30


async def step(dut, n=1):
    for _ in range(n):
        dut.clk.value = 0
        await Timer(10, "ns")
        dut.clk.value = 1
        await Timer(11, "ns")


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


@cocotb.test()
async def drive(dut):
    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    await step(dut, INITIAL_SETTLE)

    keys_str = os.environ.get("POKOY_KEYS", "")
    out_fb = os.environ.get("POKOY_OUT_FB", "/tmp/fb.bin")
    out_dump = os.environ.get("POKOY_OUT_DUMP", "/tmp/dump.txt")

    # Initial scan (before any input)
    pixels0 = await scan_display(dut)

    # Press each key
    for ch in keys_str:
        k = KEYMAP.get(ch)
        if k is None:
            continue
        await hold_key(dut, k)
    # Commit if we typed anything; also dump intermediate states
    intermediate = []
    if any(c in KEYMAP for c in keys_str):
        # COMMIT_CYCLES = 598 total
        # Sample every 10 cycles during the commit
        sample_every = int(os.environ.get("POKOY_SAMPLE_EVERY", "0"))
        if sample_every > 0:
            mem161 = dut["\\_M_00161_ "]
            cycles_done = 0
            while cycles_done < COMMIT_CYCLES:
                step_n = min(sample_every, COMMIT_CYCLES - cycles_done)
                await step(dut, step_n)
                cycles_done += step_n
                try:
                    snap = " ".join(f"{int(mem161[i].value):02x}" for i in range(64))
                except Exception as e:
                    snap = f"err {e}"
                intermediate.append((cycles_done, snap))
        else:
            await step(dut, COMMIT_CYCLES)

    pixels1 = await scan_display(dut)

    # Try to dump M_00160 and M_00161 (cipher state and display buffer)
    out_state = os.environ.get("POKOY_OUT_STATE", "/tmp/state.txt")
    state_lines = []
    # List children to discover correct names
    try:
        kids = list(dut._sub_handles.keys())[:50] if hasattr(dut, "_sub_handles") else []
        state_lines.append("kids: " + ",".join(kids[:30]))
    except Exception as e:
        state_lines.append(f"kids err {e}")
    for label, nm_try in (("M_00160", "\\_M_00160_ "), ("M_00161", "\\_M_00161_ ")):
        try:
            mem = dut[nm_try]
            vals = [int(mem[i].value) for i in range(64)]
            state_lines.append(f"{label}: " + " ".join(f"{v:02x}" for v in vals))
        except Exception as e:
            state_lines.append(f"{label}: error {e}")
    with open(out_state, "w") as f:
        f.write("\n".join(state_lines) + "\n")
        if intermediate:
            f.write("\n# Intermediate snapshots (cycle: M_00161)\n")
            for c, snap in intermediate:
                f.write(f"@{c}: {snap}\n")

    # Save both framebuffers as raw bits
    def pack(pixels):
        out = bytearray()
        for row in pixels:
            byte = 0
            cnt = 0
            for v in row:
                byte = (byte << 1) | (v & 1)
                cnt += 1
                if cnt == 8:
                    out.append(byte); byte=0; cnt=0
            if cnt:
                out.append(byte << (8-cnt))
        return bytes(out)

    with open(out_fb, "wb") as f:
        f.write(b"PRE\n")
        f.write(pack(pixels0))
        f.write(b"\nPOST\n")
        f.write(pack(pixels1))

    # Also write an ASCII dump of both frames (as 0/1)
    with open(out_dump, "w") as f:
        f.write(f"keys={keys_str!r}\n")
        f.write("PRE:\n")
        for row in pixels0:
            f.write("".join("#" if v else "." for v in row) + "\n")
        f.write("POST:\n")
        for row in pixels1:
            f.write("".join("#" if v else "." for v in row) + "\n")
    print(f"Wrote {out_fb} and {out_dump}; keys={keys_str!r}")


def main():
    os.environ["GPI_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
    os.environ["COCOTB_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
    proj_path = Path(__file__).resolve().parent
    runner = get_runner("icarus")
    runner.build(
        sources=[proj_path / "peace.v"],
        hdl_toplevel="top",
        timescale=("1ns", "1ps"),
        always=True,
    )
    runner.test(hdl_toplevel="top", test_module="drive")


if __name__ == "__main__":
    main()
