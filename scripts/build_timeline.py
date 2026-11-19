# -*- coding: utf-8 -*-
"""Xuất bảng mốc thời gian sự cố ra CSV (UTF-8 BOM, mở được bằng Excel)."""
import csv, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from incidents import INCIDENTS, COLUMNS

out = sys.argv[1] if len(sys.argv) > 1 else "01_moc_thoi_gian_su_co.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(COLUMNS)
    for r in INCIDENTS:
        w.writerow(r)
print("Đã ghi", out, len(INCIDENTS), "dòng")
