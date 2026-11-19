# -*- coding: utf-8 -*-
"""
CHẠY TOÀN BỘ QUY TRÌNH LẤY VÀ XỬ LÝ DỮ LIỆU (chạy trên máy cá nhân có Internet).

    pip install -r requirements.txt
    python chay_tat_ca.py                 # đầy đủ 2022–2025 (RIPE ~60–80 phút, M-Lab ~10 phút)
    python chay_tat_ca.py --nhanh         # chỉ lấy 7 ngày quanh mỗi sự cố (~15–20 phút)
    python chay_tat_ca.py --bo-mlab       # bỏ qua M-Lab

Kết quả nằm trong thư mục du_lieu/ và file du_lieu/DuLieu_CapQuangBien_2022_2025.xlsx
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "scripts"); D = os.path.join(HERE, "du_lieu")

def run(args):
    print("\n>>>", " ".join(args)); subprocess.run([sys.executable] + args, check=True, cwd=HERE)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true"); ap.add_argument("--bo-mlab", action="store_true")
    ap.add_argument("--bo-ripe", action="store_true", help="dùng lại du_lieu/ripe_raw.csv đã tải trước đó")
    a = ap.parse_args()
    os.makedirs(D, exist_ok=True)
    run([os.path.join(S, "build_timeline.py"), os.path.join(D, "01_moc_thoi_gian_su_co.csv")])
    raw = os.path.join(D, "ripe_raw.csv")
    if not a.bo_ripe:
        extra = ["--chi-quanh-su-co", "--so-ngay", "7"] if a.nhanh else []
        run([os.path.join(S, "lay_du_lieu_ripe_atlas.py"), "--out", raw] + extra)
    run([os.path.join(S, "xu_ly_du_lieu.py"), raw, D])
    if not a.bo_mlab:
        run([os.path.join(S, "lay_du_lieu_mlab.py"), "--out", os.path.join(D, "07_mlab_vn_theo_thang.csv")])
    run([os.path.join(S, "build_excel.py"), D, os.path.join(D, "DuLieu_CapQuangBien_2022_2025.xlsx")])
    print("\nXONG. Mở file du_lieu/DuLieu_CapQuangBien_2022_2025.xlsx")

if __name__ == "__main__":
    main()
