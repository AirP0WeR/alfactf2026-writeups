#!/usr/bin/env python3
"""Reproduce M_00324_[i] from canonical AES output _00799_ + per-block ROM mask.

From peace.v line 50740:
  _M_00324_[idx] <= {
    _00004_[127:113], _00799_[112:111], _00004_[110:85], _00799_[84],
    _00004_[83:71], _00799_[70], _00004_[69:58], _00799_[57],
    _00004_[56:51], _00799_[50], _00004_[49:0]
  }

_00004_[i] is, depending on i, either:
  - ROM_bit ^ _00799_[i]          (114 bits)
  - ~_00799_[i]                   (8 bits: positions {1,2,51,78,92,95,98,122})

ROM bits come from _M_00331_[idx] (4×114 bit). Wire-name mapping at line 52067.
"""
from pathlib import Path
import re


PEACE_V = Path(
    "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/niwhta/files/peace_6ce0fda/peace/image/src/peace.v"
)


def load_peace() -> str:
    return PEACE_V.read_text()


def extract_m00331(text: str) -> list[int]:
    """4 entries × 114 bits."""
    out = []
    for i in range(4):
        m = re.search(rf"_M_00331_\[{i}\]\s*=\s*114'h([0-9a-fA-F]+);", text)
        if not m:
            raise RuntimeError(f"no _M_00331_[{i}]")
        out.append(int(m.group(1), 16) & ((1 << 114) - 1))
    return out


def extract_wire_names(text: str) -> list[int]:
    """Return list[i] = wire-number for bit i (0..113) of the ROM word.

    Line 52067 has format: assign { name, name, ... } = _15270_;
    Leftmost name is bit [113], rightmost is bit [0].
    """
    pat = re.compile(r"assign\s*\{\s*([^\}]+)\s*\}\s*=\s*_15270_;")
    m = pat.search(text)
    if not m:
        raise RuntimeError("no _15270_ unpack assign")
    names_msb_first = [n.strip().lstrip("_").rstrip("_") for n in m.group(1).split(",")]
    names_msb_first = [int(n) for n in names_msb_first]
    if len(names_msb_first) != 114:
        raise RuntimeError(f"expected 114 wires, got {len(names_msb_first)}")
    bit_to_wirenum = list(reversed(names_msb_first))  # bit i = ...
    return bit_to_wirenum


def extract_xor_map(text: str) -> dict[int, int]:
    """For each output bit i in 0..127, return wire-number used in XOR with _00799_[i],
    or None for inverted bits (taken care of separately), or 'direct' for bits passed through.
    """
    out = {}
    for line in text.splitlines():
        m = re.match(r"\s*assign _00004_\[(\d+)\]\s*=\s*_(\d+)_\s*\^\s*_00799_\[\d+\];", line)
        if m:
            out[int(m.group(1))] = int(m.group(2))
    return out


def extract_inverted_bits(text: str) -> set[int]:
    out = set()
    for line in text.splitlines():
        m = re.match(r"\s*assign _00004_\[(\d+)\]\s*=\s*~_00799_\[\d+\];", line)
        if m:
            out.add(int(m.group(1)))
    return out


# Bits taken straight from _00799_ (no XOR) per line 50740.
DIRECT_BITS = {50, 57, 70, 84, 111, 112}


def build_mask_for_block(block_idx: int) -> tuple[int, int]:
    """Return (xor_mask, invert_mask) such that
       M_00324_[block_idx] = (_00799_ ^ xor_mask) ^ invert_mask
       where invert_mask flips the 8 fixed-inverted bits.
    """
    text = load_peace()
    rom_words = extract_m00331(text)
    bit_to_wire = extract_wire_names(text)
    xor_map = extract_xor_map(text)
    inverted = extract_inverted_bits(text)

    # wire-number → bit position in 114-bit ROM word
    wire_to_rombit = {wire: bit for bit, wire in enumerate(bit_to_wire)}

    rom_word = rom_words[block_idx]

    xor_mask = 0
    for i in range(128):
        if i in DIRECT_BITS:
            continue  # bit comes straight from _00799_, no mask
        if i in inverted:
            continue  # handled separately
        # Otherwise must be in xor_map
        wire = xor_map.get(i)
        if wire is None:
            raise RuntimeError(f"bit {i} has no source")
        rombit = wire_to_rombit.get(wire)
        if rombit is None:
            raise RuntimeError(f"wire _{wire:05d}_ not in ROM unpack")
        bit_val = (rom_word >> rombit) & 1
        if bit_val:
            xor_mask |= (1 << i)

    invert_mask = 0
    for i in inverted:
        invert_mask |= (1 << i)

    return xor_mask, invert_mask


def compute_m00324(ct_internal_bytes: bytes, block_idx: int) -> int:
    """Given canonical CT (byte 0 at MSB of register), compute M_00324_[block_idx]
    as a 128-bit int."""
    # Pack into 128-bit register, byte 0 = MSB (matches what we see in trace).
    val_799 = int.from_bytes(ct_internal_bytes, "big")
    xor_mask, invert_mask = build_mask_for_block(block_idx)
    out = (val_799 ^ xor_mask) ^ invert_mask
    return out


def m324_plaintext_for_prefix(prefix4: bytes, block_idx: int) -> bytes:
    """Build the special AES plaintext used for M_00324_[block_idx].

    In hidden/OLED mode the datapath is not AES(input_block_i).  It feeds the
    first four typed bytes into the low 32 bits and places the row/block index
    into the top byte via bits 120 and 121.  Missing this row byte makes only
    block 0 match.
    """
    if len(prefix4) != 4:
        raise ValueError("prefix4 must contain exactly 4 bytes")
    return bytes([block_idx]) + b"\x00" * 11 + bytes([prefix4[3], prefix4[2], prefix4[1], prefix4[0]])


def compute_m00324_from_prefix(prefix4: bytes, block_idx: int) -> int:
    from forward_aes import encrypt_internal_block

    return compute_m00324(encrypt_internal_block(m324_plaintext_for_prefix(prefix4, block_idx)), block_idx)


def selftest_zero():
    expected = [
        0x1b65eba8b33d56c41c3beb0dc28eccbe,
        0x08c291a7ac63eb49d8605fa03094244b,
        0x435a2ae83f247b5ff388013b3ade5f97,
        0x034dba0a5c24b38d1062ebd33460beb8,
    ]
    for i in range(4):
        got = compute_m00324_from_prefix(b"\x00\x00\x00\x00", i)
        ok = "OK" if got == expected[i] else "MISMATCH"
        print(f"M_00324_[{i}]: expected {expected[i]:032x}  got {got:032x}  {ok}")


def selftest_typed_1():
    # Input '1' typed → M_00160_[0]=0x31
    expected = [
        0x704124dc02afb5829e5fce0e79c3ddb5,
        0xe2463b22c06fc3c9935354525dacf61f,
        0x3f9fb0742680332ef085c1e7f0f153f1,
        0x1c86833bd8b5ead011f1ff64017bdbae,
    ]
    for i in range(4):
        got = compute_m00324_from_prefix(b"1\x00\x00\x00", i)
        ok = "OK" if got == expected[i] else "MISMATCH"
        print(f"[1] M_00324_[{i}]: expected {expected[i]:032x}  got {got:032x}  {ok}")


if __name__ == "__main__":
    print("--- empty input baseline ---")
    selftest_zero()
    print("--- typed '1' ---")
    selftest_typed_1()
