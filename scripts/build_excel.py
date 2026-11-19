# -*- coding: utf-8 -*-
"""Gom toàn bộ dữ liệu vào 1 file Excel. Sheet nào thiếu file nguồn thì bỏ qua."""
import sys, os, datetime as dt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(__file__))
from incidents import INCIDENTS, COLUMNS, ASSUMED_END

OUT_DIR, XLSX = sys.argv[1], sys.argv[2]
F = "Arial"
HEAD = PatternFill("solid", fgColor="1F4E79"); HFONT = Font(name=F, bold=True, color="FFFFFF", size=10)
BODY = Font(name=F, size=10); LINK = Font(name=F, size=10, color="0563C1", underline="single")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook()

def header(ws, cols, row=1):
    for j, c in enumerate(cols, 1):
        x = ws.cell(row=row, column=j, value=c); x.fill = HEAD; x.font = HFONT
        x.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center"); x.border = BOX
    ws.freeze_panes = ws.cell(row=row + 1, column=1)
    ws.auto_filter.ref = f"A{row}:{get_column_letter(len(cols))}{row}"

def widths(ws, w):
    for j, v in enumerate(w, 1): ws.column_dimensions[get_column_letter(j)].width = v

def df_sheet(name, path, w=None, date_cols=()):
    if not os.path.exists(path): return None
    df = pd.read_csv(path, encoding="utf-8-sig")
    ws = wb.create_sheet(name); header(ws, list(df.columns))
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            if isinstance(v, float) and pd.isna(v): v = None
            c = ws.cell(row=i, column=j, value=v); c.font = BODY
            if df.columns[j - 1] in date_cols and v:
                c.value = dt.date.fromisoformat(str(v)[:10]); c.number_format = "dd/mm/yyyy"
    widths(ws, w or [14] * len(df.columns)); ws.row_dimensions[1].height = 42
    return ws

# 1. Hướng dẫn
ws = wb.active; ws.title = "Huong_dan"
gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "MO_TA_DU_LIEU.md")
guide = open(gp, encoding="utf-8").read().splitlines() if os.path.exists(gp) else []
ws["A1"] = "BỘ DỮ LIỆU: SỰ CỐ CÁP QUANG BIỂN VÀ CHẤT LƯỢNG INTERNET VIỆT NAM 2022–2025"
ws["A1"].font = Font(name=F, bold=True, size=13, color="1F4E79")
for i, line in enumerate(guide, 3):
    c = ws.cell(row=i, column=1, value=line.lstrip("#").strip() if line.startswith("#") else line)
    c.font = Font(name=F, size=10, bold=line.startswith("#")); c.alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 130

# 2. Sự cố
ws = wb.create_sheet("Su_co")
cols = ["ID", "Tuyến cáp", "Nhánh / phân đoạn", "Ngày sự cố", "Độ chính xác ngày sự cố", "Ngày khôi phục",
        "Độ chính xác ngày khôi phục", "Số ngày gián đoạn", "Mức ảnh hưởng", "Ghi chú", "Nguồn 1", "Nguồn 2",
        "Loại sự kiện", "Phạm vi", "Ngày kết thúc giả định (chỉ để đếm)", "Lý do giả định"]
header(ws, cols)
for i, r in enumerate(INCIDENTS, 2):
    rec = dict(zip(COLUMNS, r))
    vals = [rec["ID"], rec["Tuyến cáp"], rec["Nhánh / phân đoạn"], rec["Ngày sự cố"], rec["Độ chính xác ngày sự cố"],
            rec["Ngày khôi phục"], rec["Độ chính xác ngày khôi phục"], None, rec["Mức ảnh hưởng"], rec["Ghi chú"],
            rec["Nguồn 1"], rec["Nguồn 2"], rec["Loại sự kiện"], rec["Phạm vi"],
            ASSUMED_END.get(rec["ID"], ("", ""))[0], ASSUMED_END.get(rec["ID"], ("", ""))[1]]
    for j, v in enumerate(vals, 1):
        c = ws.cell(row=i, column=j, value=v if v != "" else None); c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = BOX
        if j in (4, 6, 15) and v:
            c.value = dt.date.fromisoformat(v); c.number_format = "dd/mm/yyyy"
        if j in (11, 12) and v:
            c.hyperlink = v; c.font = LINK
    ws.cell(row=i, column=8, value=f'=IF(AND(ISNUMBER(D{i}),ISNUMBER(F{i})),F{i}-D{i},"")').number_format = "0"
    ws.cell(row=i, column=8).font = BODY; ws.cell(row=i, column=8).border = BOX
    if rec["Phạm vi"] == "Ngoài phạm vi":
        for j in range(1, len(cols) + 1): ws.cell(row=i, column=j).fill = PatternFill("solid", fgColor="EDEDED")
    elif rec["Loại sự kiện"] == "Hạ tầng mới":
        for j in range(1, len(cols) + 1): ws.cell(row=i, column=j).fill = PatternFill("solid", fgColor="E2EFDA")
widths(ws, [7, 9, 28, 12, 11, 12, 11, 10, 30, 48, 30, 30, 11, 13, 13, 34]); ws.row_dimensions[1].height = 45
n = len(INCIDENTS) + 3
ws.cell(row=n, column=1, value="Chú thích: nền xanh = hạ tầng mới (biến kiểm soát); nền xám = ngoài phạm vi 2022–2025, "
        "chỉ để tham khảo. Cột 'Số ngày gián đoạn' tự tính = Ngày khôi phục − Ngày sự cố. "
        "Ngày có độ chính xác 'tháng' là ước tính (ngày 15 hoặc cuối tháng).").font = Font(name=F, italic=True, size=9)

df_sheet("So_tuyen_theo_ngay", os.path.join(OUT_DIR, "05_so_tuyen_dang_su_co_theo_ngay.csv"), [12, 16, 16, 28, 34], ("ngay",))
df_sheet("RIPE_ngay_ISP", os.path.join(OUT_DIR, "04_ripe_theo_ngay_theo_isp.csv"), [12, 9, 36, 9, 13, 12, 11, 12], ("ngay",))
df_sheet("TomTat_SuCo_ISP", os.path.join(OUT_DIR, "06b_tom_tat_su_co_theo_isp.csv"), [7, 8, 12, 9, 10, 14, 14, 14, 12, 12])
df_sheet("Truoc_Trong_Sau_CapDo", os.path.join(OUT_DIR, "06_so_sanh_truoc_trong_sau.csv"), [7, 8, 12, 12, 9, 10, 10, 24, 34] + [12] * 20)
df_sheet("RIPE_theo_cap_do", os.path.join(OUT_DIR, "02_ripe_atlas_ping_theo_ngay.csv"), [12, 8, 7, 10, 10, 24, 34, 15] + [10] * 8, ("ngay",))
df_sheet("MLab_theo_thang", os.path.join(OUT_DIR, "07_mlab_vn_theo_thang.csv"))
df_sheet("Probe_RIPE", os.path.join(OUT_DIR, "03_probe_ripe_atlas.csv"), [9, 9, 8, 8, 9, 8, 20, 9, 14, 12, 12, 26])
df_sheet("Nguon_du_lieu", os.path.join(OUT_DIR, "00_nguon_du_lieu.csv"), [22, 40, 40, 30, 40])
wb.save(XLSX); print("saved", XLSX, wb.sheetnames)
