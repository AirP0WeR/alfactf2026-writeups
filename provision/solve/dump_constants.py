#!/usr/bin/env python3
"""Dump all constant tables we need for the solver."""
import openpyxl
XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"
wb = openpyxl.load_workbook(XLSX, data_only=True)  # data_only -> cached values
ws = wb["s1"]

def dump_range(top_left, bot_right, label):
    print(f"-- {label}: {top_left}:{bot_right}")
    rng = ws[f"{top_left}:{bot_right}"]
    rows = []
    for row in rng:
        r = [c.value for c in row]
        rows.append(r)
        print(r)
    return rows

# Target output
target = dump_range("A18", "H18", "target s1!A18:H18")

# B6/C6/D6 mixing (3 vectors of length 8)
m_b6 = dump_range("E40", "L40", "B6 row")
m_c6 = dump_range("E41", "L41", "C6 row")
m_d6 = dump_range("E42", "L42", "D6 row")

# Round 1 matrix M1 (8x8) and bias e1 (8)
M1 = dump_range("O30", "V37", "M1: O30:V37")
e1 = dump_range("E30", "L30", "e1: E30:L30")

# Round 2: J10 = mix of J8:Q8 via X..AE rows + B3:I3 via AG..AN rows + bias E31:L31
M2a = dump_range("X30", "AE37", "M2a: X30:AE37")  # mixes J8..Q8
M2b = dump_range("AG30", "AN37", "M2b: AG30:AN37")  # mixes B3..I3
e2 = dump_range("E31", "L31", "e2: E31:L31")

# Round 3: J12 = mix of J10:Q10 via AP..AW rows + J8:Q8 via AY..BF rows
#         + B6*E34:L34 + C6*E35:L35 + D6*E36:L36 + bias E32:L32
M3a = dump_range("AP30", "AW37", "M3a: AP30:AW37")
M3b = dump_range("AY30", "BF37", "M3b: AY30:BF37")
v34 = dump_range("E34", "L34", "v34")
v35 = dump_range("E35", "L35", "v35")
v36 = dump_range("E36", "L36", "v36")
e3 = dump_range("E32", "L32", "e3: E32:L32")
