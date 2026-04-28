#!/usr/bin/env python3
"""Decode all XOR-obfuscated MG/info blobs in the binary.

Format per func.100004000 reverse:
    [0..8]   length (uint64 LE)
    [8..16]  capacity (uint64 LE) — usually = length
    [16..]   xor stream, length bytes, key cycling [0x42, 0x13, 0x77, 0x25]

Goal: confirm names of MG-keys read in readNetworkComponents at 0x100025720 / 0x100025920.
"""

from pathlib import Path

BIN = Path(
    "tasks-2026/sealed/artifacts/dump/private/var/containers/Bundle/"
    "Application/28D38E49-69CE-47B1-A7E5-77356FEE2842/DeviceVault.app/DeviceVault"
)
data = BIN.read_bytes()
KEY = bytes([0x42, 0x13, 0x77, 0x25])

# Mach-O __DATA segment file offset = VA - 0x100000000 (no-PIE base for these binaries)
# But this binary is probably PIE; let's check by scanning. The ".v1com..."-style addresses
# are in VA space starting at 0x100000000. For Mach-O ARM64 with __DATA at 0x100020000+,
# file offset = VA - vmaddr_of_TEXT (typically 0x100000000) + filebase.
# The simplest check: search for any XOR-style blob signature anywhere by scanning
# 16-byte aligned headers where uint64 length matches reasonable string size.


def try_decode_at(file_off: int, label: str = ""):
    if file_off + 16 > len(data):
        return None
    n = int.from_bytes(data[file_off : file_off + 8], "little")
    cap = int.from_bytes(data[file_off + 8 : file_off + 16], "little")
    if not (1 <= n <= 256) or cap < n:
        return None
    payload = data[file_off + 16 : file_off + 16 + n]
    if len(payload) != n:
        return None
    decoded = bytes(b ^ KEY[i & 3] for i, b in enumerate(payload))
    if all(0x20 <= c < 0x7F for c in decoded):
        return decoded.decode("ascii", "replace")
    return None


# Try several VA→file-offset assumptions
# For typical Mach-O ARM64: __TEXT at vmaddr 0x100000000, fileoff 0
# So VA -> file_off = VA - 0x100000000
VAS_TO_TRY = [
    0x100025720,
    0x100025920,
    0x1000175d0,  # mentioned in NOTES.md
    0x100025220,  # adjacent guesses
    0x100025320,
    0x100025420,
    0x100025520,
    0x100025620,
    0x100025820,
    0x100025a20,
    # from 100008998 path — adrp x0, 0x100025000; add x0, x0, 0x720 = 0x100025720 ✓ confirmed in dv-fn-8838.txt
]

# Determine the actual VA→file map: read Mach-O LC_SEGMENT_64 commands
import struct

def parse_macho_segments():
    magic = struct.unpack("<I", data[0:4])[0]
    assert magic in (0xFEEDFACF, 0xFEEDFACE), f"unexpected magic {magic:08x}"
    ncmds = struct.unpack("<I", data[16:20])[0]
    cmds_off = 32  # 64-bit header
    segs = []
    off = cmds_off
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[off : off + 8])
        if cmd == 0x19:  # LC_SEGMENT_64
            name = data[off + 8 : off + 24].rstrip(b"\x00").decode()
            vmaddr = struct.unpack("<Q", data[off + 24 : off + 32])[0]
            vmsize = struct.unpack("<Q", data[off + 32 : off + 40])[0]
            fileoff = struct.unpack("<Q", data[off + 40 : off + 48])[0]
            segs.append((name, vmaddr, vmsize, fileoff))
        off += cmdsize
    return segs


segs = parse_macho_segments()
for name, vmaddr, vmsize, fileoff in segs:
    print(f"  {name:16s}  vm={vmaddr:#x}  size={vmsize:#x}  fileoff={fileoff:#x}")
print()


def va_to_file(va: int):
    for name, vmaddr, vmsize, fileoff in segs:
        if vmaddr <= va < vmaddr + vmsize:
            return fileoff + (va - vmaddr)
    return None


# Now scan known interesting VAs
print("== Decode at known VAs ==")
for va in VAS_TO_TRY:
    fo = va_to_file(va)
    if fo is None:
        print(f"  VA {va:#x}  not in any segment")
        continue
    decoded = try_decode_at(fo)
    print(f"  VA {va:#x}  fileoff={fo:#x}  -> {decoded!r}")
print()

# Brute scan: find ALL valid XOR blobs in __DATA / __DATA_CONST
print("== Brute scan __DATA segments for XOR-decodable strings ==")
for name, vmaddr, vmsize, fileoff in segs:
    if "DATA" not in name:
        continue
    for off in range(fileoff, fileoff + vmsize - 16, 8):
        decoded = try_decode_at(off)
        if decoded:
            va = vmaddr + (off - fileoff)
            print(f"  VA {va:#010x} ({name}): {decoded!r}")
