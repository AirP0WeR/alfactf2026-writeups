#!/usr/bin/env python3
"""Batch encryption tool. Reads JSON list of plaintext blocks (each 16 bytes hex)
from $POKOY_PT, writes ciphertext blocks to $POKOY_CT.

Strategy: bypass keypad by directly writing M_00160 contents via cocotb force,
then run COMMIT_CYCLES of clock and read M_00161.
"""
import json
import logging
import os
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


HZ = 1000
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30   # 598
INITIAL_SETTLE = 4 + 64 + 30


async def step(dut, n=1):
    for _ in range(n):
        dut.clk.value = 0
        await Timer(10, "ns")
        dut.clk.value = 1
        await Timer(11, "ns")


async def write_state(dut, plaintext64):
    """Write 64 bytes into M_00160 directly. Try multiple methods."""
    mem = dut["\\_M_00160_ "]
    # Method 1: direct .value assign at fall edge
    dut.clk.value = 0
    await Timer(5, "ns")
    for i in range(64):
        v = plaintext64[i] if i < len(plaintext64) else 0
        mem[i].value = v
    await Timer(5, "ns")
    # Print after attempt
    fails = 0
    for i in range(64):
        try:
            cur = int(mem[i].value)
            want = plaintext64[i] if i < len(plaintext64) else 0
            if cur != want:
                fails += 1
        except Exception:
            fails += 1
    if fails:
        print(f"write_state: {fails}/64 mismatches after assign")
    print(f"After write: M_00160[0]={int(mem[0].value):02x} M_00160[1]={int(mem[1].value):02x}")


async def read_ct(dut):
    """Read M_00161 (64 bytes ciphertext)."""
    mem = dut["\\_M_00161_ "]
    return bytes(int(mem[i].value) for i in range(64))


async def fake_keypress(dut, key):
    """Simulate one full keypress cycle to trigger commit logic."""
    HOLD_CYCLES = 110
    GAP_CYCLES = 110
    r, c = key // 4, key % 4
    mask = 0xF & ~(1 << c)
    last = 0xF
    for _ in range(HOLD_CYCLES):
        await step(dut, 1)
        rows = int(dut.keypad_rows.value)
        cols = mask if not ((rows >> r) & 1) else 0xF
        if cols != last:
            dut.keypad_cols.value = cols
            last = cols
    if last != 0xF:
        dut.keypad_cols.value = 0xF
    await step(dut, GAP_CYCLES)


@cocotb.test()
async def batch(dut):
    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    await step(dut, INITIAL_SETTLE)

    plaintexts = json.loads(os.environ["POKOY_PT"])  # list of hex strings (each 32 chars = 16 bytes)
    out = []
    mem160 = dut["\\_M_00160_ "]
    for ptx in plaintexts:
        # Reset between iterations to clear keypad state
        dut.resetn.value = 0
        await step(dut, 4)
        dut.resetn.value = 1
        await step(dut, INITIAL_SETTLE)

        pt = bytes.fromhex(ptx)
        pt64 = pt + b'\x00' * (64 - len(pt))
        # Trigger commit pipeline by faking keypress
        await fake_keypress(dut, 0)
        # Continuously overwrite M_00160 every cycle during commit
        for tag in range(COMMIT_CYCLES):
            for i in range(64):
                mem160[i].value = pt64[i] if i < len(pt64) else 0
            await step(dut, 1)
        before = bytes(int(mem160[i].value) for i in range(16))
        after = bytes(int(mem160[i].value) for i in range(16))
        ct = await read_ct(dut)
        out.append(ct.hex())
        print(f"PT[want]={pt[:16].hex()} pre={before.hex()} post={after.hex()} ct0={ct[:16].hex()}")

    out_path = os.environ.get("POKOY_CT", "/tmp/ct.json")
    with open(out_path, "w") as f:
        json.dump(out, f)
    print(f"Wrote {len(out)} ciphertexts to {out_path}")


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
    runner.test(hdl_toplevel="top", test_module="batch")


if __name__ == "__main__":
    main()
