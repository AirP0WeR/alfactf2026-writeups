#!/usr/bin/env python3
"""Explore different ShiftRows / byte-orderings to find readable plaintext."""
import json
from pathlib import Path

DATA = json.loads(Path('/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/pokoy/solve/aes_data.json').read_text())
ttables = DATA['ttables']
sboxes = DATA['sboxes']

AES_SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]
INV_SBOX = [0]*256
for i,v in enumerate(AES_SBOX):
    INV_SBOX[v] = i

def xtime(b): return ((b << 1) ^ (0x1b if b & 0x80 else 0)) & 0xff
def gmul(a, b):
    r = 0
    for i in range(8):
        if b & 1: r ^= a
        a = xtime(a); b >>= 1
    return r & 0xff
def build_T():
    T = [[0]*256 for _ in range(4)]
    for x in range(256):
        s = AES_SBOX[x]
        m2 = gmul(s,2); m3 = gmul(s,3)
        T[0][x] = (m2<<24)|(s<<16)|(s<<8)|m3
        T[1][x] = (m3<<24)|(m2<<16)|(s<<8)|s
        T[2][x] = (s<<24)|(m3<<16)|(m2<<8)|s
        T[3][x] = (s<<24)|(s<<16)|(m3<<8)|m2
    return T
T_AES = build_T()

tt_info = []
for ti, t in enumerate(ttables):
    for tb in range(4):
        for k_in in range(256):
            mask = t[0] ^ T_AES[tb][0 ^ k_in]
            ok = all(t[x] == (T_AES[tb][x ^ k_in] ^ mask) for x in range(256))
            if ok:
                tt_info.append((tb, k_in, mask))
                break
        else: continue
        break
sbox_info = []
for s in sboxes:
    for k_in in range(256):
        k_out = s[0] ^ AES_SBOX[k_in]
        if all(s[x] == AES_SBOX[x ^ k_in] ^ k_out for x in range(256)):
            sbox_info.append((k_in, k_out))
            break

def inv_mix_column(a):
    r = [0]*4
    r[0] = gmul(a[0],0x0e) ^ gmul(a[1],0x0b) ^ gmul(a[2],0x0d) ^ gmul(a[3],0x09)
    r[1] = gmul(a[0],0x09) ^ gmul(a[1],0x0e) ^ gmul(a[2],0x0b) ^ gmul(a[3],0x0d)
    r[2] = gmul(a[0],0x0d) ^ gmul(a[1],0x09) ^ gmul(a[2],0x0e) ^ gmul(a[3],0x0b)
    r[3] = gmul(a[0],0x0b) ^ gmul(a[1],0x0d) ^ gmul(a[2],0x09) ^ gmul(a[3],0x0e)
    return r

def round_layout(r):
    out = [[None]*4 for _ in range(4)]
    for p in range(16):
        tb, k_in, mask = tt_info[(r-1)*16 + p]
        c = p // 4
        b = tb
        out[c][b] = (k_in, mask)
    return out

def shift_rows_input(c, b):
    return ((c + b) & 3) * 4 + b

def decrypt_round(state, layout):
    new_state = [0]*16
    for c in range(4):
        col4 = state[c*4:c*4+4]
        mask_total = 0
        for b in range(4):
            _, mask = layout[c][b]
            mask_total ^= mask
        col32 = (col4[0]<<24)|(col4[1]<<16)|(col4[2]<<8)|col4[3]
        clean32 = col32 ^ mask_total
        clean = [(clean32>>24)&0xff,(clean32>>16)&0xff,(clean32>>8)&0xff,clean32&0xff]
        sbox_outs = inv_mix_column(clean)
        for b in range(4):
            k_in, _ = layout[c][b]
            new_state[shift_rows_input(c, b)] = INV_SBOX[sbox_outs[b]] ^ k_in
    return new_state

def decrypt(ct16):
    state = [0]*16
    for i in range(16):
        c, b = i//4, i%4
        k_in_i, k_out_i = sbox_info[i]
        state[shift_rows_input(c,b)] = INV_SBOX[ct16[i] ^ k_out_i] ^ k_in_i
    for r in range(9, 0, -1):
        state = decrypt_round(state, round_layout(r))
    return state

CT_HEX = """71 80 dd 08 6c 43 37 6b 3c a8 e2 68 6d 0a 97 9b
f8 23 b9 66 6a b9 92 d3 cd ad 80 cf e8 5a ed 1f
c5 c4 6c 60 c0 a3 a5 c9 11 a1 d1 98 f1 83 53 95
53 e4 b9 7c 16 5f c4 3b a3 f5 1e 12 53 1f ea ca"""
CT = [int(b, 16) for b in CT_HEX.split()]

# Decrypt all 4 blocks
pts = []
for i in range(4):
    pts.append(decrypt(CT[i*16:(i+1)*16]))

flat = sum(pts, [])
print("All bytes (block-major):")
print(' '.join(f'{b:02x}' for b in flat))
print(f"As bytes: {bytes(flat)!r}")

# Try interleaving (block 0 byte 0, block 1 byte 0, block 2 byte 0, block 3 byte 0, then block 0 byte 1, ...)
inter = []
for i in range(16):
    for b in range(4):
        inter.append(pts[b][i])
print("\nInterleaved (col-major across blocks):")
print(bytes(inter))

# Try: for each block, rearrange via inverse ShiftRows (state was in ShiftRows order)
def unshift_rows(state):
    """If state[((c+b)%4)*4+b] holds 'input at (c,b)', repack as standard 16-byte block."""
    # No wait — what does our decrypt return? It returns the round-1 INPUT state.
    # Round 1 input = pt_byte XOR (initial K0 XOR'd via ARK) — but in this implementation
    # there's no separate initial ARK; round 1's k_in absorbed K0. So our 'state' is the
    # raw plaintext byte at each state position. Let's think about state layout.
    # State[i] is just byte i of the plaintext block — no permutation needed.
    return state

# Try permutations of the 4 blocks
from itertools import permutations
print("\nSearch for ASCII-readable orderings...")
for perm in permutations(range(4)):
    cand_blocks = [pts[p] for p in perm]
    flat = sum(cand_blocks, [])
    s = bytes(flat)
    if all(32 <= c < 127 for c in s):
        print(f"perm {perm}: {s}")
        continue
    # also try column-major across blocks
    inter = []
    for i in range(16):
        for b in range(4):
            inter.append(cand_blocks[b][i])
    s2 = bytes(inter)
    if all(32 <= c < 127 for c in s2):
        print(f"perm {perm} colmajor: {s2}")

# Search wider — partial readability
print("\n=== Counting printable per block ===")
for i, p in enumerate(pts):
    printable = sum(1 for c in p if 32 <= c < 127)
    print(f"Block {i}: {printable}/16 printable. bytes={bytes(p)!r}")

# Maybe we should try without ShiftRows assumption (try all positions 0..15 mapped identity)
def shift_rows_identity(c, b):
    return c*4 + b

def decrypt_round_alt(state, layout, sr_func):
    new_state = [0]*16
    for c in range(4):
        col4 = state[c*4:c*4+4]
        mask_total = 0
        for b in range(4):
            _, mask = layout[c][b]
            mask_total ^= mask
        col32 = (col4[0]<<24)|(col4[1]<<16)|(col4[2]<<8)|col4[3]
        clean32 = col32 ^ mask_total
        clean = [(clean32>>24)&0xff,(clean32>>16)&0xff,(clean32>>8)&0xff,clean32&0xff]
        sbox_outs = inv_mix_column(clean)
        for b in range(4):
            k_in, _ = layout[c][b]
            new_state[sr_func(c, b)] = INV_SBOX[sbox_outs[b]] ^ k_in
    return new_state

def decrypt_alt(ct16, sr_func):
    state = [0]*16
    for i in range(16):
        c, b = i//4, i%4
        k_in_i, k_out_i = sbox_info[i]
        state[sr_func(c,b)] = INV_SBOX[ct16[i] ^ k_out_i] ^ k_in_i
    for r in range(9, 0, -1):
        state = decrypt_round_alt(state, round_layout(r), sr_func)
    return state

print("\n=== Try identity shift rows (no permutation) ===")
for i in range(4):
    p = decrypt_alt(CT[i*16:(i+1)*16], shift_rows_identity)
    printable = sum(1 for c in p if 32 <= c < 127)
    print(f"Block {i}: {printable}/16 printable. bytes={bytes(p)!r}")

# Try "inverse" ShiftRows: ((c-b)%4)*4 + b
def shift_rows_inv(c, b):
    return ((c - b) & 3) * 4 + b

print("\n=== Try inverse ShiftRows ===")
for i in range(4):
    p = decrypt_alt(CT[i*16:(i+1)*16], shift_rows_inv)
    printable = sum(1 for c in p if 32 <= c < 127)
    print(f"Block {i}: {printable}/16 printable. bytes={bytes(p)!r}")
