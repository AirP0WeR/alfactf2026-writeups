#!/usr/bin/env python3
import openpyxl
XLSX = "/Users/airp0wer/Projects/alfa-ctf-2026/tasks-2026/provision/artifacts/provision.xlsx"
wb = openpyxl.load_workbook(XLSX, data_only=False)
ws = wb["s1"]
for coord in ["B3","C3","D3","E3","F3","G3","H3","I3","B2","B4"]:
    c = ws[coord]
    v = c.value
    print(coord, type(v).__name__, end=" ")
    if hasattr(v, 'text'):
        print("text=", v.text, "ref=", v.ref)
    else:
        print(repr(v))
