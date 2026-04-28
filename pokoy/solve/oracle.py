#!/usr/bin/env python3
"""Black-box oracle: drive peace.v with a key sequence and read 64-byte display.

Usage as cocotb test module. Set env var POKOY_KEYS to a string like '1234*#abc'.
Reads display state after each commit (or just final). Writes pixels and decoded
hex to stdout.
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
HZ = 1000
HOLD_CYCLES = 110 * HZ // 1000
GAP_CYCLES = 110 * HZ // 1000
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30
INITIAL_SETTLE = 4 + 64 + 30

KEYMAP = {
    "1": 0,  "2": 1,  "3": 2,  "a": 3,  "A": 3,
    "4": 4,  "5": 5,  "6": 6,  "b": 7,  "B": 7,
    "7": 8,  "8": 9,  "9": 10, "c": 11, "C": 11,
    "*": 12, "0": 13, "#": 14, "d": 15, "D": 15,
}


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
        # bits is a BinaryValue; iterate as little-endian 0..127
        s = bits.binstr  # MSB-first, 128 chars
        # We want pixel[c] for c=0..127 to be bit c of scan_pixels
        for c in range(128):
            pixels[i][c] = int(s[127 - c])
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


def pixels_to_quadrants(pixels):
    BLOCKS = {
        0b0000: " ", 0b0001: "▗", 0b0010: "▖", 0b0011: "▄",
        0b0100: "▝", 0b0101: "▐", 0b0110: "▞", 0b0111: "▟",
        0b1000: "▘", 0b1001: "▚", 0b1010: "▌", 0b1011: "▙",
        0b1100: "▀", 0b1101: "▜", 0b1110: "▛", 0b1111: "█",
    }
    rows = []
    for y in range(0, HEIGHT, 2):
        row = []
        for x in range(0, WIDTH, 2):
            idx = (pixels[y][x] << 3) | (pixels[y][x + 1] << 2) \
                | (pixels[y + 1][x] << 1) | pixels[y + 1][x + 1]
            row.append(BLOCKS[idx])
        rows.append("".join(row))
    return "\n".join(rows)


def parse_key_chars(s):
    out = []
    for ch in s:
        if ch in KEYMAP:
            out.append(KEYMAP[ch])
    return out


@cocotb.test()
async def run_oracle(dut):
    keys_env = os.environ.get("POKOY_KEYS", "")
    keys = parse_key_chars(keys_env)
    sys.stderr.write(f"[oracle] driving {len(keys)} keys: {keys_env!r}\n")
    sys.stderr.flush()

    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    await step(dut, INITIAL_SETTLE)

    # Initial display
    pixels = await scan_display(dut)
    sys.stderr.write("[oracle] initial display:\n")
    sys.stderr.write(pixels_to_quadrants(pixels) + "\n")
    sys.stderr.flush()

    for i, k in enumerate(keys):
        await hold_key(dut, k)
        # commit window (the python loop normally waits 0.4s for repeat
        # presses; here we just always commit immediately since each press
        # is its own commit)
        await step(dut, COMMIT_CYCLES)

    pixels = await scan_display(dut)
    sys.stdout.write("FINAL_DISPLAY:\n")
    sys.stdout.write(pixels_to_quadrants(pixels) + "\n")
    sys.stdout.flush()


def main():
    os.environ["GPI_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
    os.environ["COCOTB_LOG_LEVEL"] = logging.getLevelName(logging.WARNING)
    proj_path = Path("/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/pokoy/files/peace_6ce0fda/peace/image/src")
    runner = get_runner("icarus")
    runner.build(
        sources=[proj_path / "peace.v"],
        hdl_toplevel="top",
        timescale=("1ns", "1ps"),
        always=True,
    )
    runner.test(hdl_toplevel="top", test_module="oracle", test_dir=Path(__file__).parent)


if __name__ == "__main__":
    main()
