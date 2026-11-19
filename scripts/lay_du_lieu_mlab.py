# -*- coding: utf-8 -*-
"""
Lấy số liệu M-Lab NDT (thống kê theo tháng, theo ISP) cho Việt Nam, 2022–2025.

Nguồn: M-Lab "Monthly Stats" (dự án IQB) – file Parquet công khai trên Google Cloud
Storage, không cần tài khoản BigQuery. Danh sách file lấy từ manifest trong repo
github.com/m-lab/iqb (data/state/ghremote/manifest.json).

Cách chạy (Windows / macOS / Linux, Python 3.9+):
    pip install pandas pyarrow requests
    python lay_du_lieu_mlab.py
Kết quả: mlab_vn_theo_thang.csv (cả nước + VNPT, Viettel, FPT; mỗi tháng 1 dòng/đối tượng).
Dung lượng tải: khoảng 9 MB/tháng x 48 tháng (chỉ chiều tải xuống) ~ 430 MB.
Thêm tham số --upload để lấy thêm tốc độ tải lên (gấp đôi dung lượng tải).

LƯU Ý ĐỌC SỐ LIỆU (theo tài liệu M-Lab IQB):
- download_pN: phân vị N của tốc độ tải xuống (Mbit/s), p50 = trung vị.
- latency_pN, loss_pN: phân vị "theo chất lượng" – p1 là nhóm 1% KÉM nhất, p99 là tốt
  nhất; p50 vẫn là trung vị. latency tính bằng ms (MinRTT), loss là tỉ lệ (0–1).
- Phép đo NDT kết nối tới máy chủ M-Lab gần nhất; với người dùng Việt Nam phần lớn
  máy chủ nằm ngoài lãnh thổ, nên số liệu phản ánh chủ yếu đường đi quốc tế.
"""
import argparse, io, sys, time
import pandas as pd
import requests

MANIFEST = "https://raw.githubusercontent.com/m-lab/iqb/main/data/state/ghremote/manifest.json"
ISP = {45899: "VNPT", 7552: "Viettel", 18403: "FPT"}

def months(y0=2022, y1=2025):
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            a = f"{y}{m:02d}01T000000Z"
            b = f"{y + (m == 12)}{(m % 12) + 1:02d}01T000000Z"
            yield f"{y}-{m:02d}", a, b

def get(url, tries=3):
    for k in range(tries):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            return r.content
        except Exception as e:
            print("  lỗi:", e, "- thử lại", k + 1); time.sleep(5 * (k + 1))
    raise RuntimeError("Không tải được " + url)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true", help="lấy thêm tốc độ tải lên")
    ap.add_argument("--out", default="mlab_vn_theo_thang.csv")
    args = ap.parse_args()
    files = requests.get(MANIFEST, timeout=60).json()["files"]
    rows = []
    for ym, a, b in months():
        for kind in (["downloads", "uploads"] if args.upload else ["downloads"]):
            for sl in ("by_country", "by_country_asn"):
                key = f"cache/v1/{a}/{b}/{kind}_{sl}/data.parquet"
                if key not in files:
                    print("thiếu", key); continue
                print(ym, kind, sl)
                df = pd.read_parquet(io.BytesIO(get(files[key]["url"])))
                df = df[df["country_code"] == "VN"].copy()
                if sl == "by_country_asn":
                    df["asn"] = pd.to_numeric(df["asn"].astype(str).str.replace("AS", "", regex=False),
                                              errors="coerce")
                    df = df[df["asn"].isin(ISP)]
                    df["doi_tuong"] = df["asn"].map(ISP)
                else:
                    df["asn"] = None
                    df["doi_tuong"] = "Cả nước"
                df.insert(0, "thang", ym)
                df.insert(1, "chieu", "tai_xuong" if kind == "downloads" else "tai_len")
                rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    print("Đã ghi", args.out, len(out), "dòng")

if __name__ == "__main__":
    main()
