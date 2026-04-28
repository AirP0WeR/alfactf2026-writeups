#!/usr/bin/env python3
import logging
import os
import select
import sys
import termios
import tty
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


WIDTH = 128
HEIGHT = 64

# Quadrant block glyphs: 4 pixels (2x2) per glyph, bits = TL TR BL BR.
BLOCKS = {
    0b0000: " ", 0b0001: "▗", 0b0010: "▖", 0b0011: "▄",
    0b0100: "▝", 0b0101: "▐", 0b0110: "▞", 0b0111: "▟",
    0b1000: "▘", 0b1001: "▚", 0b1010: "▌", 0b1011: "▙",
    0b1100: "▀", 0b1101: "▜", 0b1110: "▛", 0b1111: "█",
}

# Terminal key → input index (row*4+col) for the 4x4 grid:
#     1 2 3 A    -> 0  1  2  3
#     4 5 6 B    -> 4  5  6  7
#     7 8 9 C    -> 8  9 10 11
#     * 0 # D    -> 12 13 14 15
KEYMAP = {
    "1": 0,  "2": 1,  "3": 2,  "a": 3,  "A": 3,
    "4": 4,  "5": 5,  "6": 6,  "b": 7,  "B": 7,
    "7": 8,  "8": 9,  "9": 10, "c": 11, "C": 11,
    "*": 12, "0": 13, "#": 14, "d": 15, "D": 15,
}

# Must match the HZ value peace.v was built with. HOLD/GAP are sized so a
# single press is registered exactly once at this clock rate.
HZ = 1000
HOLD_CYCLES = 110 * HZ // 1000
GAP_CYCLES = 110 * HZ // 1000
# After each commit (or reset) the design runs an internal pipeline before
# the next display read becomes valid. Wait the design's own commit timeout
# plus that pipeline.
COMMIT_CYCLES = HZ // 2 + 4 + 64 + 30
# The same pipeline must run once after reset before the first scan,
# otherwise the readout samples X-valued state.
INITIAL_SETTLE = 4 + 64 + 30


class TUI:
    def __init__(self):
        self.queue = []
        self.running = True
        self.status = "ready"
        self.typed = ""


async def step(dut, n=1):
    # Manual clock stepping. There's no free-running cocotb.Clock task —
    # the simulator only advances when we call this. While the main loop
    # is parked on stdin the simulator is completely idle.
    for _ in range(n):
        dut.clk.value = 0
        await Timer(10, "ns")
        dut.clk.value = 1
        await Timer(11, "ns")


def poll_stdin(tui):
    # Drain anything currently buffered without blocking.
    while select.select([sys.stdin], [], [], 0)[0]:
        data = os.read(sys.stdin.fileno(), 1)
        if not data:
            tui.running = False
            return
        ch = data.decode(errors="ignore")
        if ch == "\x03":  # Ctrl-C
            tui.running = False
            return
        k = KEYMAP.get(ch)
        if k is not None:
            tui.queue.append((k, ch))


def wait_for_input(tui, timeout):
    # Block the python thread (and therefore the simulator) until stdin has
    # something or `timeout` seconds elapse.
    r, _, _ = select.select([sys.stdin], [], [], timeout)
    if r:
        poll_stdin(tui)


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


def render(pixels, tui):
    out = ["\033[H"]
    for y in range(0, HEIGHT, 2):
        row = []
        for x in range(0, WIDTH, 2):
            idx = (pixels[y][x] << 3) | (pixels[y][x + 1] << 2) \
                | (pixels[y + 1][x] << 1) | pixels[y + 1][x + 1]
            row.append(BLOCKS[idx])
        out.append("".join(row))
        out.append("\033[K\n")
    out.append("\033[K\n")
    out.append("keys: 1-9 0 * # a b c d   (Ctrl-C to quit)\033[K\n")
    out.append(f"status: {tui.status}\033[K\n")
    out.append(f"typed:  {tui.typed[-64:]}\033[K")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


async def hold_key(dut, key):
    # Hold `key` for HOLD_CYCLES then release for GAP_CYCLES. Cols are
    # driven active-low only while the corresponding row is being read,
    # otherwise the input would be ambiguous and never register.
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
async def peace(dut):
    dut.clk.value = 0
    dut.resetn.value = 0
    dut.keypad_cols.value = 0xF
    dut.scan_valid.value = 0
    dut.scan_row.value = 0
    await step(dut, 10)
    dut.resetn.value = 1
    # Let the design's internal pipeline populate the framebuffer before
    # the first scan; otherwise scan_pixels samples X-valued state.
    await step(dut, INITIAL_SETTLE)

    tui = TUI()

    old = None
    if sys.stdin.isatty():
        old = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
    sys.stdout.write("\033[?25l\033[2J\033[H")
    sys.stdout.flush()

    try:
        pixels = await scan_display(dut)
        render(pixels, tui)
        dirty = False

        while tui.running:
            poll_stdin(tui)

            if tui.queue:
                key, label = tui.queue.pop(0)
                tui.typed += label
                tui.status = f"typing '{label}' (q={len(tui.queue)})"
                render(pixels, tui)
                await hold_key(dut, key)
                dirty = True
                continue

            if dirty:
                # Repeat-press window. Park the sim and wait briefly for
                # another keystroke; if it arrives, treat it as a follow-up
                # press. Otherwise commit and redraw.
                tui.status = "..."
                render(pixels, tui)
                wait_for_input(tui, 0.4)
                if tui.queue:
                    continue
                tui.status = "committing"
                render(pixels, tui)
                await step(dut, COMMIT_CYCLES)
                pixels = await scan_display(dut)
                dirty = False
                tui.status = "ready"
                render(pixels, tui)
                continue

            tui.status = "ready"
            render(pixels, tui)
            wait_for_input(tui, 5.0)
    finally:
        tui.running = False
        if old is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


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
    runner.test(hdl_toplevel="top", test_module="peace")


if __name__ == "__main__":
    old = None
    if sys.stdin.isatty():
        old = termios.tcgetattr(sys.stdin.fileno())
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        if old is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
