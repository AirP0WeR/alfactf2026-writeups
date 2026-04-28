#!/usr/bin/env python3
"""T5: Build forward and inverse encrypt/decrypt primitives using the
EXTRACTED tables directly — no need to recover canonical AES key.

Approach:
  state[16] = pt (initial 16 bytes).
  For each round r in 1..9:
      For each column c in 0..3:
          col4 = XOR of T_(r, c*4 + b)[ state[input_byte_for(r,c,b)] ] for b in 0..3
      new_state[c*4..c*4+3] = bytes(col4) (as big-endian 4 bytes)
  state = new_state
  Final: out[i] = sbox_i[ state[input_for_final(i)] ]

The input_byte_for(r,c,b) is determined by ShiftRows: state[((c+b)%4)*4 + b].
We just need to verify this layout produces the correct CT for some pt. But we don't
have a known pt/ct pair! Trick: use the sim/oracle. Or: invert algebraically.

Let me invert directly. Each ttable is invertible (256 inputs -> 256 distinct outputs)
for fixed (tb, k_in, mask). To decrypt:

For final round: state[input_for_final(i)] = sbox_inv_i[ ct[i] ]
   sbox_i[x] = AES_SBOX[x XOR k_in_i] XOR k_out_i, so
   sbox_inv[y] = AES_INV_SBOX[y XOR k_out_i] XOR k_in_i

For round r (going backwards): given the 16-byte output state of round r,
   the column c (4 bytes) = XOR of 4 ttable outputs.
   Each T_(r, c*4+b)[input] is a 32-bit value. XOR of 4 = column. To invert,
   we need to know the input bytes. But the inputs are state bytes from round r-1.

For a single column we have 4 unknowns (the 4 input state bytes) and 4 byte equations
(the column 32-bit value). Each ttable T_(r, c*4+b)[x] = T_b[x XOR k_in] XOR mask.
This is a non-linear (S-box) function of x. So inverting directly is not just XOR.

Trick: the 4 inputs to a column come from 4 different state bytes (one from each
column of input state), and they each go to all 4 output columns (because of ShiftRows).
So 16 input bytes -> 16 output bytes is a bijection composed of 4 column-mixers.

Each column-mixer: 4 bytes in -> 4 bytes out, where each output byte position is
a XOR of components depending on each input byte.

Specifically for output column c, byte row b:
  out[c*4+b] = XOR over b' in 0..3 of T_b'[in[((c+b')%4)*4 + b'] XOR k_in_(r,c*4+b')] [byte b]

Wait, let me re-derive. T_b is the AES T-table column for input position row b (the row determines which AES T_b table to use). The 4 ttables for a single output column c read from inputs at:
  b=0: state[((c+0)%4)*4 + 0] = state[c*4 + 0]
  b=1: state[((c+1)%4)*4 + 1]
  b=2: state[((c+2)%4)*4 + 2]
  b=3: state[((c+3)%4)*4 + 3]

These are 4 DIFFERENT input bytes (one per row). So each input byte feeds INTO exactly
one ttable and contributes a 4-byte vector. To invert: unknown input bytes, observed
column 4-byte vector. Each T_b is invertible (it's a permutation in x), so:
   given the 4-byte output column, we want to find 4 input bytes a,b,c,d such that
   T_0(a) XOR T_1(b) XOR T_2(c) XOR T_3(d) = column.

This is generally NOT trivially invertible in 256^4. But we can use AES MixColumns invertibility:
   T0(s0) XOR T1(s1) XOR T2(s2) XOR T3(s3) = MixColumns(SBox(s0)||SBox(s1)||SBox(s2)||SBox(s3))
So column = MC(SBoxes). Apply InvMixColumns: get SBox(s_i) for i=0..3. Apply InvSBox: get s_i.

But we have masks that XOR with each output. So before InvMC we need to XOR out the mask:
  observed_column = T_0(a^k0) XOR mask0 XOR T_1(b^k1) XOR mask1 XOR T_2(c^k2) XOR mask2 XOR T_3(d^k3) XOR mask3
                  = XOR of T's XOR (mask0^mask1^mask2^mask3)
                  = column_clean XOR XORmask_total

where column_clean = T_0(a^k0) ^ T_1(b^k1) ^ T_2(c^k2) ^ T_3(d^k3).
column_clean = MC( SBox(a^k0), SBox(b^k1), SBox(c^k2), SBox(d^k3) ).

So:
  1. column_clean = observed XOR XOR-of-4-masks
  2. apply InvMC to column_clean -> 4 SBox outputs
  3. apply InvSBox -> a^k0, b^k1, c^k2, d^k3
  4. XOR with k_in's -> recover input state bytes a, b, c, d at their respective positions.

Now the input positions a,b,c,d are at state indices (c*4+0), ((c+1)%4)*4+1, ((c+2)%4)*4+2, ((c+3)%4)*4+3.

That gives us complete decryption!
"""
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

def xtime(b):
    return ((b << 1) ^ (0x1b if b & 0x80 else 0)) & 0xff
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
        m2 = gmul(s, 2); m3 = gmul(s, 3)
        T[0][x] = (m2 << 24) | (s << 16) | (s << 8) | m3
        T[1][x] = (m3 << 24) | (m2 << 16) | (s << 8) | s
        T[2][x] = (s << 24) | (m3 << 16) | (m2 << 8) | s
        T[3][x] = (s << 24) | (s << 16) | (m3 << 8) | m2
    return T
T_AES = build_T()

# Recover (tb, k_in, mask) for all 144 ttables
tt_info = []
for ti, t in enumerate(ttables):
    for tb in range(4):
        for k_in in range(256):
            mask = t[0] ^ T_AES[tb][0 ^ k_in]
            ok = all(t[x] == (T_AES[tb][x ^ k_in] ^ mask) for x in range(256))
            if ok:
                tt_info.append((tb, k_in, mask))
                break
        else:
            continue
        break
assert len(tt_info) == 144

# Recover (k_in, k_out) for final sboxes
sbox_info = []
for s in sboxes:
    for k_in in range(256):
        k_out = s[0] ^ AES_SBOX[k_in]
        if all(s[x] == AES_SBOX[x ^ k_in] ^ k_out for x in range(256)):
            sbox_info.append((k_in, k_out))
            break

# Layout of T-tables in chip output:
#   For round r, position p (0..15), the ttable is tt_info[(r-1)*16 + p].
#   Within the round, positions (4c..4c+3) form output column c.
#   The b-th ttable in column c uses tb that we recovered.
#   In standard AES T-table layout, tb=b for all positions, so column c byte b uses T_b.
#   But we observed tb pattern: pos 0=tb0, pos1=tb1, pos2=tb2, pos3=tb3 (column 0 - standard)
#                              pos 4=tb0, pos5=tb1, pos6=tb2, pos7=tb3 (column 1 - standard)
#                              pos 8=tb2, pos9=tb3, pos10=tb0, pos11=tb1 (column 2 - reordered!)
#                              pos12=tb2, pos13=tb3, pos14=tb0, pos15=tb1 (column 3 - reordered!)
# So positions 8-15 have tb shifted by 2. This tells us the COLUMN for pos 8..11 has b'th ttable
# at position 8+(b shifted). Actually it tells us: at chip-position p, tb=table_index. If we
# group by column, tb cycles. The chip just stores tables in a different order — we need to map
# chip-position p to (output_column c, output_row b).
#
# Let's interpret: the 16 chip positions p map to (c, b) pairs. From tb pattern:
#   p=0,(c=0,b=0); p=1,(0,1); p=2,(0,2); p=3,(0,3); p=4,(1,0); p=5,(1,1); p=6,(1,2); p=7,(1,3);
#   p=8,(2,2); p=9,(2,3); p=10,(2,0); p=11,(2,1); p=12,(3,2); p=13,(3,3); p=14,(3,0); p=15,(3,1).
# Wait that's reading tb as 'b', then column is determined externally.

# Let me re-parameterize. For output column c, the 4 ttables have tb=(0,1,2,3) in some order.
# In chip storage, columns 0,1 have tb order (0,1,2,3); columns 2,3 have (2,3,0,1).
# This is just a storage detail; the COMBINATION (XOR of 4 ttables in a column) is the same
# regardless of order. So we can group chip-positions into columns:
COLUMNS = [
    [0,1,2,3],     # col 0
    [4,5,6,7],     # col 1
    [8,9,10,11],   # col 2
    [12,13,14,15], # col 3
]

# For each chip-position p in column c, we now know its tb (from extraction) and that
# determines which row b the ttable processes. And the input byte is state[((c+b)%4)*4 + b]
# under standard ShiftRows. Let's lock that in and test.

def shift_rows_input(c, b):
    """state index that feeds T_b for column c output (standard AES ShiftRows)."""
    return ((c + b) & 3) * 4 + b

# Build per-round info: for each chip-position p (0..15), record (column c, row b, k_in, mask, tb)
def round_layout(r):
    """r=1..9. Returns list of 16 dicts indexed by output column c, sub-index b."""
    out = [[None]*4 for _ in range(4)]  # out[c][b] = (k_in, mask)
    for p in range(16):
        tb, k_in, mask = tt_info[(r-1)*16 + p]
        c = p // 4
        b = tb  # output row within column = tb
        out[c][b] = (k_in, mask)
    return out

# Forward encryption: state_bytes -> state_bytes
def encrypt_round(state, layout):
    """One full round: 4 columns, each output by XOR of 4 ttables.
    state: list of 16 bytes.
    layout: result of round_layout(r). layout[c][b] = (k_in, mask).
    Returns new 16 bytes.
    """
    new_state = [0]*16
    for c in range(4):
        column32 = 0
        for b in range(4):
            k_in, mask = layout[c][b]
            inp_idx = shift_rows_input(c, b)
            inp = state[inp_idx]
            t_val = T_AES[b][inp ^ k_in] ^ mask
            column32 ^= t_val
        # column32 packed big-endian: byte b at position c*4 + b
        new_state[c*4 + 0] = (column32 >> 24) & 0xff
        new_state[c*4 + 1] = (column32 >> 16) & 0xff
        new_state[c*4 + 2] = (column32 >> 8) & 0xff
        new_state[c*4 + 3] = column32 & 0xff
    return new_state

def encrypt(pt16):
    state = list(pt16)
    for r in range(1, 10):
        layout = round_layout(r)
        state = encrypt_round(state, layout)
    # final round: 16 sboxes; chip-position i uses sbox i. Input byte: ShiftRows on i.
    # Final layout in standard AES: out[c*4+b] = SBOX[state[((c+b)%4)*4 + b]] XOR K10[c*4+b]
    # The chip stores 16 sboxes with k_in (= state byte XOR'd before AES_SBOX) and k_out.
    # Position i in chip -> (c, b)? Maybe just direct: i = c*4+b. Let me try.
    out = [0]*16
    for i in range(16):
        c, b = i // 4, i % 4
        inp_idx = shift_rows_input(c, b)
        k_in_i, k_out_i = sbox_info[i]
        out[i] = AES_SBOX[state[inp_idx] ^ k_in_i] ^ k_out_i
    return out

# Inverse round
INV_MC_MUL = (0x0e, 0x0b, 0x0d, 0x09)
def inv_mix_column(col4):
    a = col4
    r = [0]*4
    r[0] = gmul(a[0],0x0e) ^ gmul(a[1],0x0b) ^ gmul(a[2],0x0d) ^ gmul(a[3],0x09)
    r[1] = gmul(a[0],0x09) ^ gmul(a[1],0x0e) ^ gmul(a[2],0x0b) ^ gmul(a[3],0x0d)
    r[2] = gmul(a[0],0x0d) ^ gmul(a[1],0x09) ^ gmul(a[2],0x0e) ^ gmul(a[3],0x0b)
    r[3] = gmul(a[0],0x0b) ^ gmul(a[1],0x0d) ^ gmul(a[2],0x09) ^ gmul(a[3],0x0e)
    return r

def decrypt_round(state, layout):
    """Invert one round. Given the OUTPUT state, return INPUT state."""
    new_state = [0]*16
    for c in range(4):
        # observed column 32-bit
        col4 = state[c*4:c*4+4]
        # XOR away mask combination
        mask_total = 0
        for b in range(4):
            _, mask = layout[c][b]
            mask_total ^= mask
        col32 = (col4[0]<<24) | (col4[1]<<16) | (col4[2]<<8) | col4[3]
        clean32 = col32 ^ mask_total
        clean = [(clean32>>24)&0xff, (clean32>>16)&0xff, (clean32>>8)&0xff, clean32&0xff]
        # apply InvMixColumns to get SBox outputs
        sbox_outs = inv_mix_column(clean)
        # apply InvSBox to get x XOR k_in for each row b
        for b in range(4):
            xkin = INV_SBOX[sbox_outs[b]]
            k_in, _ = layout[c][b]
            input_byte = xkin ^ k_in
            inp_idx = shift_rows_input(c, b)
            new_state[inp_idx] = input_byte
    return new_state

def decrypt(ct16):
    # invert final round first
    state = [0]*16
    # final: out[i] = SBOX[state_in[ShiftRows(i)] XOR k_in_i] XOR k_out_i
    # state_in[ShiftRows(i)] = INV_SBOX[ ct[i] XOR k_out_i ] XOR k_in_i
    for i in range(16):
        c, b = i // 4, i % 4
        inp_idx = shift_rows_input(c, b)
        k_in_i, k_out_i = sbox_info[i]
        state[inp_idx] = INV_SBOX[ct16[i] ^ k_out_i] ^ k_in_i
    # invert rounds 9..1
    for r in range(9, 0, -1):
        layout = round_layout(r)
        state = decrypt_round(state, layout)
    return state

# Test: encrypt then decrypt zero block
test_pt = [0]*16
ct = encrypt(test_pt)
back = decrypt(ct)
print(f"PT  : {' '.join(f'{b:02x}' for b in test_pt)}")
print(f"CT  : {' '.join(f'{b:02x}' for b in ct)}")
print(f"BACK: {' '.join(f'{b:02x}' for b in back)}")
print(f"Round-trip OK: {back == test_pt}")

# Now decrypt the actual 4 CT blocks
CT_HEX = """71 80 dd 08 6c 43 37 6b 3c a8 e2 68 6d 0a 97 9b
f8 23 b9 66 6a b9 92 d3 cd ad 80 cf e8 5a ed 1f
c5 c4 6c 60 c0 a3 a5 c9 11 a1 d1 98 f1 83 53 95
53 e4 b9 7c 16 5f c4 3b a3 f5 1e 12 53 1f ea ca"""
CT = [int(b, 16) for b in CT_HEX.split()]
assert len(CT) == 64

print("\n=== Decrypted plaintext (4 blocks of 16) ===")
for i in range(4):
    block = CT[i*16:(i+1)*16]
    pt = decrypt(block)
    print(f"Block {i}: {' '.join(f'{b:02x}' for b in pt)}  ascii: {bytes(pt)!r}")
