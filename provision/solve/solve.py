#!/usr/bin/env python3
"""
Solver for «Учёт провизии» (Alfa CTF 2026).

Layout (all on hidden sheet `s1`):
  - User types 8 chars into Panel!Z6, AD6, AH6, AL6, AP6, AT6, AX6, BB6.
  - s1!B2:I2 mirror those, s1!B3:I3 look up ASCII via s1!A23:B48 (a-z -> 97-122).
  - s1!B4:I4 = (B3>0)  -> 8 ones means all chars are in [a-z] (Panel COUNTIF #1).
  - s1!B6, C6, D6 = MOD(SUMPRODUCT(x, row_E40/E41/E42), 251).
  - s1!J8..Q8     = MOD(M1 . x + e1, 251),                                M1=O30:V37, e1=E30:L30
  - s1!J10..Q10   = MOD(M2a . y8 + M2b . x + e2, 251),                    M2a=X30:AE37, M2b=AG30:AN37, e2=E31:L31
  - s1!J12..Q12   = MOD(M3a . y10 + M3b . y8 + b6*v34 + c6*v35 + d6*v36 + e3, 251)
                    M3a=AP30:AW37, M3b=AY30:BF37, v34=E34:L34, v35=E35:L35, v36=E36:L36, e3=E32:L32
  - target s1!A18:H18 = [92, 97, 27, 240, 199, 80, 217, 23]
  - s1!J14:Q14 = (J12==target). All eight must be 1 (Panel COUNTIF #2).

So we have 8 equations mod 251 in 8 unknowns x[i] in [97, 122]. Z3 makes it trivial.
"""

import openpyxl
from z3 import Solver, Int, And, Or, Sum, sat

XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"

wb = openpyxl.load_workbook(XLSX, data_only=True)
s1 = wb["s1"]

def grab(top, bot):
    return [[c.value for c in row] for row in s1[f"{top}:{bot}"]]

target = [int(v) for v in grab("A18", "H18")[0]]
m_b6 = [int(v) for v in grab("E40", "L40")[0]]
m_c6 = [int(v) for v in grab("E41", "L41")[0]]
m_d6 = [int(v) for v in grab("E42", "L42")[0]]
M1 = [[int(v) for v in r] for r in grab("O30", "V37")]
e1 = [int(v) for v in grab("E30", "L30")[0]]
M2a = [[int(v) for v in r] for r in grab("X30", "AE37")]
M2b = [[int(v) for v in r] for r in grab("AG30", "AN37")]
e2 = [int(v) for v in grab("E31", "L31")[0]]
M3a = [[int(v) for v in r] for r in grab("AP30", "AW37")]
M3b = [[int(v) for v in r] for r in grab("AY30", "BF37")]
v34 = [int(v) for v in grab("E34", "L34")[0]]
v35 = [int(v) for v in grab("E35", "L35")[0]]
v36 = [int(v) for v in grab("E36", "L36")[0]]
e3 = [int(v) for v in grab("E32", "L32")[0]]

print("target y12 =", target)

s = Solver()
x = [Int(f"x{i}") for i in range(8)]
for xi in x:
    s.add(xi >= 97, xi <= 122)

# y8[k] = (sum_i M1[k][i]*x[i] + e1[k]) mod 251
y8 = [Int(f"y8_{k}") for k in range(8)]
for k in range(8):
    raw = Sum([M1[k][i]*x[i] for i in range(8)]) + e1[k]
    s.add(y8[k] >= 0, y8[k] < 251, (raw - y8[k]) % 251 == 0)

# y10[k] = (sum M2a[k][i]*y8[i] + sum M2b[k][i]*x[i] + e2[k]) mod 251
y10 = [Int(f"y10_{k}") for k in range(8)]
for k in range(8):
    raw = (Sum([M2a[k][i]*y8[i] for i in range(8)]) +
           Sum([M2b[k][i]*x[i] for i in range(8)]) + e2[k])
    s.add(y10[k] >= 0, y10[k] < 251, (raw - y10[k]) % 251 == 0)

# b6 = sum(m_b6[i]*x[i]) mod 251 (and similar for c6, d6)
def mod251(expr, name):
    v = Int(name)
    s.add(v >= 0, v < 251, (expr - v) % 251 == 0)
    return v
b6 = mod251(Sum([m_b6[i]*x[i] for i in range(8)]), "b6")
c6 = mod251(Sum([m_c6[i]*x[i] for i in range(8)]), "c6")
d6 = mod251(Sum([m_d6[i]*x[i] for i in range(8)]), "d6")

# y12[k] = (sum M3a[k][i]*y10[i] + sum M3b[k][i]*y8[i] + b6*v34[k] + c6*v35[k] + d6*v36[k] + e3[k]) mod 251
for k in range(8):
    raw = (Sum([M3a[k][i]*y10[i] for i in range(8)]) +
           Sum([M3b[k][i]*y8[i] for i in range(8)]) +
           b6*v34[k] + c6*v35[k] + d6*v36[k] + e3[k])
    s.add((raw - target[k]) % 251 == 0)

print("solving...")
res = s.check()
print(res)
if res == sat:
    m = s.model()
    chars = [m[xi].as_long() for xi in x]
    pw = "".join(chr(c) for c in chars)
    print("password ASCII:", chars)
    print("password:", pw)
    print("flag candidate:", "alfa{" + pw + "}")
