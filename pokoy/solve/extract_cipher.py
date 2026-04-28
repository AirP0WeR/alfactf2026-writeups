#!/usr/bin/env python3
"""Extract cipher structure from peace.v netlist into a Python module.

Output: cipher.json with:
  - sboxes: 16 inverse-final-round permutations (256-byte arrays)
  - ttables: 144 32-bit T-tables (256 entries each)
  - rounds[k] for k in 0..8: list of 128 entries, each describing how _0080(k+1)[bit_i] is computed.
    Each entry is {polarity, terms: [(table_idx, bit), ...]} where table_idx is 0..143.
  - final[i] for i in 0..15: {input_byte, output_byte, sbox_idx} describing the SBox lookup.

Use these to:
  - encrypt: for each round, compute new state from current state by XORing T-table outputs.
  - decrypt: invert.
"""
import re
import sys
import json
from collections import defaultdict


def parse_netlist(path):
    lines = open(path).readlines()

    # 8-bit memory inits (sboxes)
    re_sbox_init = re.compile(r"\\_M_(\d{5})_\s+\[(\d+)\] = 8'h([0-9a-f]+);")
    sboxes = {}
    for line in lines:
        m = re_sbox_init.search(line)
        if m:
            nm = m.group(1)
            idx = int(m.group(2))
            v = int(m.group(3), 16)
            n = int(nm)
            if n < 16:
                sboxes.setdefault(nm, [0]*256)[idx] = v

    # 32-bit T-table inits
    re_t_dec = re.compile(r"\\_M_(\d{5})_\s+\[(\d+)\] = 32'd(\d+);")
    re_t_hex = re.compile(r"\\_M_(\d{5})_\s+\[(\d+)\] = 32'h([0-9a-f]+);")
    ttables = {}
    for line in lines:
        m = re_t_dec.search(line)
        if m:
            nm = m.group(1)
            idx = int(m.group(2))
            v = int(m.group(3))
            ttables.setdefault(nm, [0]*256)[idx] = v
            continue
        m = re_t_hex.search(line)
        if m:
            nm = m.group(1)
            idx = int(m.group(2))
            v = int(m.group(3), 16)
            ttables.setdefault(nm, [0]*256)[idx] = v

    # Parse T-table reads to get bit-name <-> (tt_name, bit_pos) mapping
    re_tt_read = re.compile(r"assign \{([^}]+)\}\s*=\s*\\_M_(\d{5})_\s+\[(\w+)\[(\d+):(\d+)\]\];")
    bit_to_tt = {}
    table_input = {}  # tt_name -> (signal, byte_idx)
    for line in lines:
        m = re_tt_read.search(line)
        if m:
            wires = [w.strip() for w in m.group(1).split(',')]
            nm = m.group(2)
            sig = m.group(3)
            hi = int(m.group(4))
            lo = int(m.group(5))
            byte_idx = lo // 8
            for j, w in enumerate(wires):
                bit_pos = 31 - j
                bit_to_tt[w] = (nm, bit_pos)
            table_input[nm] = (sig, byte_idx)

    # Parse SBox reads (final round)
    re_sbox_read = re.compile(r"assign\s+(\S+)\s*=\s*\\_M_(\d{5})_\s+\[(\w+)\[(\d+):(\d+)\]\];")
    final_round = []
    for line in lines:
        m = re_sbox_read.search(line)
        if m:
            target = m.group(1)
            nm = m.group(2)
            n = int(nm)
            if n >= 16:
                continue
            sig = m.group(3)
            hi = int(m.group(4))
            lo = int(m.group(5))
            in_byte = lo // 8
            # parse target: e.g. '_00799_[127:120]'
            mt = re.match(r"(\w+)\[(\d+):(\d+)\]", target)
            if not mt:
                continue
            tgt_sig = mt.group(1)
            tgt_hi = int(mt.group(2))
            tgt_lo = int(mt.group(3))
            out_byte = tgt_lo // 8
            final_round.append({
                'sbox': nm,
                'in_signal': sig,
                'in_byte': in_byte,
                'out_signal': tgt_sig,
                'out_byte': out_byte,
            })

    # Parse all "assign WIRE = EXPR;" definitions
    re_wire_assign = re.compile(r"^\s*assign\s+(\S+)\s*=\s*(.+?);\s*$")
    wire_def = {}
    for line in lines:
        m = re_wire_assign.match(line)
        if m:
            w = m.group(1).strip()
            expr = m.group(2).strip()
            wire_def[w] = expr  # last def wins (should be unique)

    return sboxes, ttables, bit_to_tt, table_input, final_round, wire_def


def balanced(s):
    d = 0
    for c in s:
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        if d < 0:
            return False
    return d == 0


def split_top(s, op):
    parts = []
    cur = ''
    d = 0
    for c in s:
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        if c == op and d == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += c
    parts.append(cur.strip())
    return parts


def parse_expr(expr, base_wires_set):
    """Parse expression. Returns (xor_set_of_base_wires, polarity_bit)."""
    expr = expr.strip()
    while expr.startswith('(') and expr.endswith(')') and balanced(expr[1:-1]):
        expr = expr[1:-1].strip()
    if expr.startswith('~'):
        s, p = parse_expr(expr[1:], base_wires_set)
        return s, 1 - p
    parts = split_top(expr, '^')
    if len(parts) > 1:
        rs = set()
        rp = 0
        for part in parts:
            s, p = parse_expr(part, base_wires_set)
            # XOR sets: symmetric difference
            rs = rs.symmetric_difference(s)
            rp ^= p
        return rs, rp
    # Atom: either constant or wire
    m = re.match(r"^(\d+)'([hdb])([0-9a-f]+)$", expr)
    if m:
        base = m.group(2)
        v = int(m.group(3), {'h': 16, 'd': 10, 'b': 2}[base])
        return set(), v & 1
    return {expr}, 0


def expand(wire, wire_def, bit_to_tt, memo):
    if wire in memo:
        return memo[wire]
    if wire in bit_to_tt:
        memo[wire] = ({wire}, 0)
        return memo[wire]
    if wire not in wire_def:
        memo[wire] = ({wire}, 0)
        return memo[wire]
    expr = wire_def[wire]
    base_set, polar = parse_expr(expr, bit_to_tt)
    out_wires = set()
    out_pol = polar
    for bw in base_set:
        s, p = expand(bw, wire_def, bit_to_tt, memo)
        out_wires = out_wires.symmetric_difference(s)
        out_pol ^= p
    memo[wire] = (out_wires, out_pol)
    return memo[wire]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'peace.v'
    sboxes, ttables, bit_to_tt, table_input, final_round, wire_def = parse_netlist(path)
    print(f"Sboxes: {len(sboxes)} T-tables: {len(ttables)} bit_to_tt: {len(bit_to_tt)} wires: {len(wire_def)}")

    # For each round k (0..8), enumerate output state _0080(k+1)
    # And describe each output bit as XOR of T-table output bits.
    sys.setrecursionlimit(200000)
    memo = {}
    rounds = []
    for k in range(9):
        # Output is _0080(k+1)
        target_sig = f"_0080{k+1}_"
        bit_assigns = {}
        for w, expr in wire_def.items():
            m = re.match(r"^" + target_sig + r"\[(\d+)\]$", w)
            if m:
                bit_assigns[int(m.group(1))] = expr
        if not bit_assigns:
            print(f"Round {k}: no bit assigns for {target_sig}!")
            rounds.append([])
            continue
        # Expand each bit
        round_data = []
        for bit in range(128):
            expr = bit_assigns.get(bit)
            if expr is None:
                round_data.append({'polarity': 0, 'terms': []})
                continue
            base_set, polar = parse_expr(expr, bit_to_tt)
            out_wires = set()
            out_pol = polar
            for bw in base_set:
                s, p = expand(bw, wire_def, bit_to_tt, memo)
                out_wires = out_wires.symmetric_difference(s)
                out_pol ^= p
            terms = []
            for w in out_wires:
                if w in bit_to_tt:
                    terms.append(bit_to_tt[w])
                else:
                    print(f"WARN: round {k} bit {bit}: unresolved wire {w}")
            terms.sort()
            round_data.append({'polarity': out_pol, 'terms': terms})
        rounds.append(round_data)
        # Stats: how many terms per bit?
        nterms = [len(r['terms']) for r in round_data]
        from collections import Counter
        print(f"Round {k}: {len(round_data)} bits, term-count dist: {Counter(nterms)}")

    # Save
    out = {
        'sboxes': sboxes,
        'ttables': ttables,
        'table_input': {k: list(v) for k, v in table_input.items()},
        'rounds': rounds,
        'final_round': final_round,
    }
    with open('cipher.json', 'w') as f:
        json.dump(out, f)
    print("written cipher.json")


if __name__ == '__main__':
    main()
