#!/usr/bin/env python3
"""Probe T9 multi-tap mapping: support tap counts via key,count pairs."""
import logging
import os
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


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


def parse_seq(s):
    """Parse 'k1[,n1] k2[,n2] ...' OR comma-list 'a,3 b,1' OR plain string with optional repeat marks like 'a3 b1'.

    Use format: 'CHAR*COUNT CHAR*COUNT ...' separated by spaces.
    e.g. '2*1 2*2 a*3' = press '2' once, then '2' twice (multi-tap), then 'a' three times.
    Each 'group' is a multi-tap commit.
    """
    out = []
    for tok in s.split():
        if "*" in tok:
            ch, n = tok.split("*", 1)
            n = int(n)
        else:
            ch, n = tok, 1
        if ch in KEYMAP:
            out.append((KEYMAP[ch], n, ch))
    return out


@cocotb.test()
async def probe(dut):
    seq_env = os.environ.get("POKOY_SEQ", "")
    seq = parse_seq(seq_env)

    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    await step(dut, INITIAL_SETTLE)

    mem160 = getattr(dut, "\\_M_00160_ ")

    sys.stderr.write(f"[probe2] seq: {seq_env!r}\n")
    sys.stderr.flush()

    for key, n, ch in seq:
        for _ in range(n):
            await hold_key(dut, key)
        await step(dut, COMMIT_CYCLES)

    vals = [int(mem160[i].value) for i in range(64)]
    sys.stdout.write(" ".join(f"{v:02x}" for v in vals) + "\n")
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
    runner.test(hdl_toplevel="top", test_module="probe2", test_dir=Path(__file__).parent)


if __name__ == "__main__":
    main()
