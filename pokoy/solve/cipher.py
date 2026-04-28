#!/usr/bin/env python3
"""Pure Python cipher: encrypt and decrypt one 16-byte block.

Loads structure from cipher.json (created by extract_cipher.py).

Encryption flow:
  state0 = plaintext (16 bytes -> 128 bits, with byte i at bit positions 8i..8i+7)
  for k in 0..8:
    For each bit j of state(k+1):
      bit = polarity[k][j] XOR sum(term in terms[k][j]: T_table[term.tt][state(k)[term.byte_idx]] >> term.bit & 1)
  Then final round: for each (sbox_M_NNN, in_byte, out_byte):
    ciphertext[out_byte] = sbox[state9[in_byte]]

For efficiency, each round can be vectorized: compute all 16 T-table outputs (32-bit each)
from state(k)'s 16 bytes, then for each of 128 output bits XOR the relevant T-table bits.
"""
import json


def load_cipher(path='cipher.json'):
    with open(path) as f:
        return json.load(f)


def state_byte(state_bits, byte_idx):
    """Extract byte byte_idx from a 128-bit int. Byte i = bits [8i..8i+7]."""
    return (state_bits >> (8 * byte_idx)) & 0xFF


def encrypt_block(plaintext_16bytes, cipher_data, debug=False):
    sboxes = cipher_data['sboxes']
    ttables = cipher_data['ttables']
    table_input = cipher_data['table_input']
    rounds = cipher_data['rounds']
    final_round = cipher_data['final_round']

    # Initial state: 128-bit int from plaintext bytes (byte 0 -> bits 0..7, byte 15 -> bits 120..127)
    state = 0
    for i, b in enumerate(plaintext_16bytes):
        state |= b << (8 * i)

    # 9 rounds
    for k in range(9):
        # Compute 16 T-table outputs (each 32 bits) for this round
        # Tables for round k are M_(16+16k) .. M_(16+16k+15)
        tt_outputs = {}  # tt_name (5-digit) -> 32-bit value
        for tt_idx in range(16):
            tt_name = f"{16 + 16*k + tt_idx:05d}"
            input_byte_idx = table_input[tt_name][1]
            input_byte = state_byte(state, input_byte_idx)
            tt_outputs[tt_name] = ttables[tt_name][input_byte]
        # Compute each bit of next state
        new_state = 0
        round_def = rounds[k]
        for bit_pos in range(128):
            entry = round_def[bit_pos]
            polarity = entry['polarity']
            bit = polarity & 1
            for tt_name, tt_bit in entry['terms']:
                v = (tt_outputs[tt_name] >> tt_bit) & 1
                bit ^= v
            new_state |= bit << bit_pos
        state = new_state

    # Final round: 16 sboxes
    ciphertext = bytearray(16)
    for fr in final_round:
        sbox_name = fr['sbox']
        in_byte = state_byte(state, fr['in_byte'])
        ciphertext[fr['out_byte']] = sboxes[sbox_name][in_byte]
    return bytes(ciphertext)


def decrypt_block(ciphertext_16, cipher_data):
    """Invert the cipher. Each round is invertible via 4-T-table MITM.

    Final round inversion: for each fr, sbox[state9[in_byte]] = ct[out_byte] ⇒ state9[in_byte] = inv_sbox[ct[out_byte]].

    Round k inversion: state(k+1) is known. We need state(k).
        Per byte, state(k+1) is 8 bits, and these bits are described as XORs of T-table bits.
        We need to recover 16 bytes of state(k) such that the round-forward gives state(k+1).
    """
    sboxes = cipher_data['sboxes']
    ttables = cipher_data['ttables']
    table_input = cipher_data['table_input']
    rounds = cipher_data['rounds']
    final_round = cipher_data['final_round']

    # Step 1: invert final SBox round
    state = [0] * 16  # state9 bytes (in_byte indexed)
    for fr in final_round:
        sbox = sboxes[fr['sbox']]
        ct_byte = ciphertext_16[fr['out_byte']]
        # find x such that sbox[x] == ct_byte
        # build inverse once
        inv = [0] * 256
        for x, y in enumerate(sbox):
            inv[y] = x
        x = inv[ct_byte]
        state[fr['in_byte']] = x

    # state is state9 (16 bytes), bit-packed by byte_idx
    state_bits = 0
    for i, b in enumerate(state):
        state_bits |= b << (8 * i)

    # Step 2..10: invert rounds 8 down to 0.
    # For each round k, we have state(k+1) bits and want state(k) bytes.
    # state(k+1) is computed from state(k) via 16 T-tables and combine.
    # For each output column (4 output bytes = 32 bits), the inputs are 4 specific input bytes.
    # We use MITM: for each pair (input_byte_a, input_byte_b), compute partial XOR; for each pair (input_byte_c, input_byte_d), compute the rest. Match.
    #
    # But first we need to identify the column structure: which 4 input-byte indices map to each 32-bit column?
    # Each T-table outputs to specific output bits. Let's group: for each input byte idx, find which output bits are influenced (XOR'd with that table).

    for k in range(8, -1, -1):
        round_def = rounds[k]
        # Identify columns: groups of 32 output bits that share the same set of 4 input T-tables
        # We use which T-tables appear in the terms.
        # For each output bit j, we have list of (tt_name, tt_bit) tuples (4 of them).
        # The set of distinct tt_names across consecutive bits gives us the column.
        # In our case, we observe AES-like 32-bit columns.
        from collections import defaultdict
        # Group bits by their 4-table set
        bit_to_tableset = []
        for j in range(128):
            entry = round_def[j]
            tts = tuple(sorted({t[0] for t in entry['terms']}))
            bit_to_tableset.append(tts)
        unique_groups = list(set(bit_to_tableset))
        if k >= 8 and False:
            print(f"Round {k}: {len(unique_groups)} distinct table-sets")
        # For each unique group, find the 32 bits that have that group, sort them.
        groups = defaultdict(list)
        for j, tt_set in enumerate(bit_to_tableset):
            groups[tt_set].append(j)
        if any(len(v) != 32 for v in groups.values()):
            raise SystemExit(f"Round {k}: groups don't all have 32 bits: {[len(v) for v in groups.values()]}")
        # For each group: the 4 input bytes are the table_input[tt][1] of the 4 tables.
        new_state_bytes = [None] * 16
        for tt_set, bits in groups.items():
            # 4 tables, 4 input bytes
            tt_list = list(tt_set)
            in_byte_idxs = [table_input[tt][1] for tt in tt_list]
            # Get 32-bit target value
            target = 0
            for j in bits:
                bit_v = (state_bits >> j) & 1
                # Map j to its position within the column (0..31). We need a canonical ordering.
                # Use the smallest bit in the group as offset.
                pass
            # Determine for each bit the contribution per table:
            #   target_bit_j = polarity[j] ^ sum_{(tt,b) in terms[j]} T[tt][in_byte_v_for_tt] bit b
            # We iterate input candidates over (tt0, tt1) pairs and compute partial,
            # for (tt2, tt3) compute partial, match.
            # For each 32-bit column, we have 4 tables; we know which output bit j comes from which 4 (tt, bit) tuples.
            # First, compute target = XOR_{j in bits} (output_bit_j << index_in_col)
            # But we need a consistent indexing. Let's just compare bit-wise against the table outputs.

            # Build for each tt, function: in_byte -> 32-bit "contribution to column" (with bit position adjusted)
            # i.e. contrib[tt][x] = XOR over (j, jbit) in terms_with_tt: ((T[tt][x] >> jbit) & 1) << j
            contrib = {}
            polarity_acc = 0
            for tt in tt_list:
                cmap = [0] * 256
                # Collect for each output bit j in this group, the tt_bit positions corresponding to this tt
                # bit j is in column at offset bits.index(j) (we'll index columns via 0..31)
                # Actually better: we just keep absolute bit position j and shift T[tt][x]'s bit appropriately.
                # The bits in 'bits' are arbitrary positions; we work in absolute bit-space.
                bit_pos_to_ttbit = {}
                for j in bits:
                    # find term in round_def[j].terms with tt_name == tt
                    for (n, b) in round_def[j]['terms']:
                        if n == tt:
                            bit_pos_to_ttbit[j] = b
                            break
                if len(bit_pos_to_ttbit) != 32:
                    raise SystemExit(f"Round {k} group {tt_set}: tt {tt} only contributes to {len(bit_pos_to_ttbit)} bits")
                for x in range(256):
                    tv = ttables[tt][x]
                    cont = 0
                    for j, b in bit_pos_to_ttbit.items():
                        cont |= ((tv >> b) & 1) << j
                    cmap[x] = cont
                contrib[tt] = cmap
            # Polarity: XOR over j in bits of polarity[j], placed at bit j
            # equivalent absolute integer P
            P = 0
            for j in bits:
                P |= round_def[j]['polarity'] << j
            # Target values are state_bits masked to these bit positions
            target_mask = 0
            for j in bits:
                target_mask |= 1 << j
            target = state_bits & target_mask
            # We want: P ^ contrib[tt0][x0] ^ contrib[tt1][x1] ^ contrib[tt2][x2] ^ contrib[tt3][x3] == target
            # ⇒ contrib[tt0][x0] ^ contrib[tt1][x1] = target ^ P ^ contrib[tt2][x2] ^ contrib[tt3][x3]
            # MITM
            # left: 256*256 entries
            left = {}
            for x0 in range(256):
                for x1 in range(256):
                    v = contrib[tt_list[0]][x0] ^ contrib[tt_list[1]][x1]
                    left.setdefault(v, []).append((x0, x1))
            # right: 256*256
            target_p = target ^ P
            found = None
            for x2 in range(256):
                c2 = contrib[tt_list[2]][x2]
                for x3 in range(256):
                    v = target_p ^ c2 ^ contrib[tt_list[3]][x3]
                    if v in left:
                        for (x0, x1) in left[v]:
                            found = (x0, x1, x2, x3)
                            break
                        if found:
                            break
                if found:
                    break
            if not found:
                raise SystemExit(f"Round {k}: no inverse found for column with tables {tt_set}")
            # Set the input bytes
            xs = found
            for i, tt in enumerate(tt_list):
                idx = in_byte_idxs[i]
                if new_state_bytes[idx] is not None and new_state_bytes[idx] != xs[i]:
                    raise SystemExit(f"Round {k}: conflicting input byte {idx}: {new_state_bytes[idx]} vs {xs[i]}")
                new_state_bytes[idx] = xs[i]

        # Reconstruct state(k) bits
        if any(b is None for b in new_state_bytes):
            raise SystemExit(f"Round {k}: missing input byte indices: {[i for i,v in enumerate(new_state_bytes) if v is None]}")
        new_state_bits = 0
        for i, b in enumerate(new_state_bytes):
            new_state_bits |= b << (8 * i)
        state_bits = new_state_bits

    # state_bits is now state0 = plaintext
    pt = bytearray(16)
    for i in range(16):
        pt[i] = (state_bits >> (8 * i)) & 0xFF
    return bytes(pt)


if __name__ == '__main__':
    import sys
    cd = load_cipher()
    if len(sys.argv) > 1 and sys.argv[1] == 'enc':
        # encrypt 16 bytes hex
        pt = bytes.fromhex(sys.argv[2])
        ct = encrypt_block(pt, cd)
        print(ct.hex())
    elif len(sys.argv) > 1 and sys.argv[1] == 'dec':
        ct = bytes.fromhex(sys.argv[2])
        pt = decrypt_block(ct, cd)
        print(pt.hex())
    else:
        # Self-test: encrypt(0x00...00) should match the known empty-block ciphertext
        pt = bytes(16)
        ct = encrypt_block(pt, cd)
        print(f"enc(00*16) = {ct.hex()}")
        expected = bytes.fromhex("b815ae0200d3636cdc813748d784793e")
        print(f"expected   = {expected.hex()}")
        print(f"match: {ct == expected}")
