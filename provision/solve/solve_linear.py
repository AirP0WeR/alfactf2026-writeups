#!/usr/bin/env python3
"""
Direct linear-algebra solver mod 251 for «Учёт провизии».

Insight: y12 is linear in x mod 251 (b6, c6, d6 are each linear-in-x scalars
multiplied by constant vectors v34/v35/v36, so the products are linear in x).
So the entire system is one 8x8 linear system over F_251 — solve via Gaussian
elimination, then check that all x[i] fall into [97, 122].
"""

import openpyxl

XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"
P = 251

wb = openpyxl.load_workbook(XLSX, data_only=True)
s1 = wb["s1"]

def grab(top, bot):
    return [[c.value for c in row] for row in s1[f"{top}:{bot}"]]

target = [int(v) for v in grab("A18", "H18")[0]]
m_b6 = [int(v) for v in grab("E40", "L40")[0]]
m_c6 = [int(v) for v in grab("E41", "L41")[0]]
m_d6 = [int(v) for v in grab("E42", "L42")[0]]
M1   = [[int(v) for v in r] for r in grab("O30", "V37")]
e1   = [int(v) for v in grab("E30", "L30")[0]]
M2a  = [[int(v) for v in r] for r in grab("X30", "AE37")]
M2b  = [[int(v) for v in r] for r in grab("AG30", "AN37")]
e2   = [int(v) for v in grab("E31", "L31")[0]]
M3a  = [[int(v) for v in r] for r in grab("AP30", "AW37")]
M3b  = [[int(v) for v in r] for r in grab("AY30", "BF37")]
v34  = [int(v) for v in grab("E34", "L34")[0]]
v35  = [int(v) for v in grab("E35", "L35")[0]]
v36  = [int(v) for v in grab("E36", "L36")[0]]
e3   = [int(v) for v in grab("E32", "L32")[0]]


def matmul(A, B):
    """A (a x b) * B (b x c) -> (a x c) mod P."""
    a = len(A); b = len(A[0]); c = len(B[0])
    out = [[0]*c for _ in range(a)]
    for i in range(a):
        for j in range(c):
            s = 0
            for k in range(b):
                s += A[i][k] * B[k][j]
            out[i][j] = s % P
    return out

def matadd(A, B):
    return [[(A[i][j] + B[i][j]) % P for j in range(len(A[0]))] for i in range(len(A))]

def matvec(A, v):
    return [sum(A[i][j]*v[j] for j in range(len(v))) % P for i in range(len(A))]

# Identity 8x8
I8 = [[1 if i==j else 0 for j in range(8)] for i in range(8)]

# y8 = M1 . x + e1
A_y8 = [row[:] for row in M1]
c_y8 = e1[:]

# y10 = M2a . y8 + M2b . x + e2
#      = (M2a . M1 + M2b) . x + (M2a . e1 + e2)
A_y10 = matadd(matmul(M2a, A_y8), M2b)
c_y10 = [(matvec(M2a, c_y8)[i] + e2[i]) % P for i in range(8)]

# u_k = b6*v34[k] + c6*v35[k] + d6*v36[k]
# b6 = sum m_b6[i]*x[i] (no constant)
# So u is a rank-? linear combination: u_k = sum_i (m_b6[i]*v34[k] + m_c6[i]*v35[k] + m_d6[i]*v36[k]) * x[i]
A_u = [[(m_b6[i]*v34[k] + m_c6[i]*v35[k] + m_d6[i]*v36[k]) % P for i in range(8)] for k in range(8)]

# y12 = M3a . y10 + M3b . y8 + u + e3
A_y12 = matadd(matadd(matmul(M3a, A_y10), matmul(M3b, A_y8)), A_u)
c_y12_no_e3 = [(matvec(M3a, c_y10)[i] + matvec(M3b, c_y8)[i]) % P for i in range(8)]
c_y12 = [(c_y12_no_e3[i] + e3[i]) % P for i in range(8)]

# We need A_y12 . x + c_y12 == target  (mod P)
# => A_y12 . x = (target - c_y12) mod P
b = [(target[i] - c_y12[i]) % P for i in range(8)]

# Solve A_y12 . x = b mod P using Gaussian elimination.
def modinv(a, p=P):
    return pow(a, -1, p)

def gauss_solve(A, b, p=P):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        # find pivot
        piv = None
        for r in range(col, n):
            if M[r][col] % p != 0:
                piv = r; break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        inv = modinv(M[col][col] % p, p)
        for j in range(col, n+1):
            M[col][j] = (M[col][j] * inv) % p
        for r in range(n):
            if r == col: continue
            f = M[r][col] % p
            if f == 0: continue
            for j in range(col, n+1):
                M[r][j] = (M[r][j] - f*M[col][j]) % p
    return [M[i][n] % p for i in range(n)]

x = gauss_solve(A_y12, b)
print("x mod 251:", x)
if x is None:
    print("No unique solution mod 251.")
else:
    pw_chars = []
    ok = True
    for xi in x:
        if 97 <= xi <= 122:
            pw_chars.append(chr(xi))
        else:
            ok = False
            pw_chars.append(f"<{xi}>")
    print("password chars:", pw_chars)
    if ok:
        pw = "".join(pw_chars)
        print("password:", pw)
        print("flag candidate:", "alfa{" + pw + "}")
    else:
        print("Solution outside [97,122] — re-check matrix extraction.")

# Sanity check: plug x back and recompute y12 to confirm == target
if x is not None:
    y8_chk  = [(sum(M1[k][i]*x[i] for i in range(8)) + e1[k]) % P for k in range(8)]
    y10_chk = [(sum(M2a[k][i]*y8_chk[i] for i in range(8)) +
                sum(M2b[k][i]*x[i] for i in range(8)) + e2[k]) % P for k in range(8)]
    b6 = sum(m_b6[i]*x[i] for i in range(8)) % P
    c6 = sum(m_c6[i]*x[i] for i in range(8)) % P
    d6 = sum(m_d6[i]*x[i] for i in range(8)) % P
    y12_chk = [(sum(M3a[k][i]*y10_chk[i] for i in range(8)) +
                sum(M3b[k][i]*y8_chk[i] for i in range(8)) +
                b6*v34[k] + c6*v35[k] + d6*v36[k] + e3[k]) % P for k in range(8)]
    print("y12 recomputed:", y12_chk)
    print("target        :", target)
    print("match:", y12_chk == target)
