# -*- coding: utf-8 -*-
"""
Lấy số liệu ping từ các probe RIPE Atlas đặt tại Việt Nam (VNPT, Viettel, FPT),
2022–2025, và tổng hợp theo ngày: độ trễ (RTT), jitter, tỉ lệ mất gói.

Cách lấy mẫu (giống bộ dữ liệu nhóm đã thu): mỗi ngày lấy cửa sổ 1 giờ cao điểm
20:00–21:00 giờ Việt Nam (13:00–14:00 UTC). Có thể đổi bằng tham số --gio-utc.

Cách chạy:
    pip install requests
    python lay_du_lieu_ripe_atlas.py                # toàn bộ 2022–2025 (lâu, ~1–1,5 giờ)
    python lay_du_lieu_ripe_atlas.py --tu 2023-01-15 --den 2023-03-15   # một cửa sổ sự cố
Kết quả: ripe_atlas_ping_theo_ngay.csv

API công khai, không cần tài khoản: https://atlas.ripe.net/docs/apis/rest-api-manual/
"""
import argparse, csv, datetime as dt, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import requests

PROBES = {  # probe_id: (ISP, ASN)
    1000379: ("VNPT", 45899), 21640: ("VNPT", 45899), 1000382: ("VNPT", 45899),
    28050: ("VNPT", 45899), 1005516: ("VNPT", 45899), 1006856: ("VNPT", 45899),
    1009020: ("VNPT", 45899), 1011222: ("VNPT", 45899), 1013301: ("VNPT", 45899),
    411: ("FPT", 18403), 54440: ("FPT", 18403), 1000388: ("FPT", 18403),
    1003518: ("FPT", 18403), 64251: ("FPT", 18403), 1009312: ("FPT", 18403),
    55753: ("Viettel", 7552), 7400: ("Viettel", 7552), 1008882: ("Viettel", 7552),
}
# msm_id: (đích, nhóm, ngày bắt đầu có dữ liệu)
MSMS = {
    1001: ("k.root-servers.net", "root_anycast", "2022-01-01"),
    1004: ("f.root-servers.net", "root_anycast", "2022-01-01"),
    1011: ("c.root-servers.net", "root_anycast", "2022-01-01"),
    18854725: ("sg-sin-as55002 anchor", "Singapore", "2022-01-01"),
    23871798: ("sg-sin-as16276 anchor", "Singapore", "2022-01-01"),
    29781560: ("sg-sin-as12008 anchor", "Singapore", "2022-01-01"),
    40447822: ("sg-sin-as38001 anchor", "Singapore", "2022-04-26"),
    25787843: ("us-lax-as3491 anchor", "My_LosAngeles", "2022-01-01"),
    26070042: ("tw-tpe-as3491 anchor", "DongBacA", "2022-01-01"),
    25313148: ("kr-sel-as20473 anchor", "DongBacA", "2022-01-01"),
    63883300: ("hk-hkg-as32167 anchor", "HongKong", "2023-11-22"),
}
API = "https://atlas.ripe.net/api/v2/measurements/{m}/results/"
COLS = ["ngay", "probe_id", "isp", "asn", "msm_id", "dich", "nhom_dich", "dst_addr",
        "so_lan_do", "goi_gui", "goi_nhan", "mat_goi_pct", "rtt_min_ms", "rtt_trungvi_ms",
        "rtt_p95_ms", "jitter_ms"]

def pct(a, p):
    if not a: return ""
    s = sorted(a); return round(s[min(len(s) - 1, int(p * (len(s) - 1) + 0.5))], 2)

def one(day, m, hour):
    s = int(dt.datetime(day.year, day.month, day.day, hour, tzinfo=dt.timezone.utc).timestamp())
    params = {"probe_ids": ",".join(map(str, PROBES)), "start": s, "stop": s + 3600}
    for k in range(3):
        try:
            r = requests.get(API.format(m=m), params=params, timeout=60)
            if r.status_code in (400, 404): return []
            r.raise_for_status(); data = r.json(); break
        except Exception:
            time.sleep(3 * (k + 1))
    else:
        return [("LOI", day, m)]
    g = {}
    for x in data: g.setdefault(x["prb_id"], []).append(x)
    out = []
    for p, arr in g.items():
        arr.sort(key=lambda x: x["timestamp"])
        sent = sum(x.get("sent", 0) for x in arr); rcvd = sum(x.get("rcvd", 0) for x in arr)
        rtts = [y["rtt"] for x in arr for y in x.get("result", []) if isinstance(y.get("rtt"), (int, float))]
        jit = round(sum(abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))) / (len(rtts) - 1), 2) if len(rtts) > 1 else ""
        isp, asn = PROBES.get(p, ("?", ""))
        out.append([day.isoformat(), p, isp, asn, m, MSMS[m][0], MSMS[m][1], arr[0].get("dst_addr", ""),
                    len(arr), sent, rcvd, round(100 * (sent - rcvd) / sent, 2) if sent else "",
                    pct(rtts, 0), pct(rtts, .5), pct(rtts, .95), jit])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tu", default="2022-01-01"); ap.add_argument("--den", default="2025-12-31")
    ap.add_argument("--gio-utc", type=int, default=13, help="giờ UTC bắt đầu cửa sổ 1 giờ (13 = 20h VN)")
    ap.add_argument("--chi-quanh-su-co", action="store_true",
                    help="chỉ lấy các ngày quanh sự cố (N ngày trước, N ngày đầu, N ngày sau khôi phục)")
    ap.add_argument("--so-ngay", type=int, default=14, help="độ dài mỗi cửa sổ quanh sự cố (ngày)")
    ap.add_argument("--luong", type=int, default=8); ap.add_argument("--out", default="ripe_atlas_ping_theo_ngay.csv")
    a = ap.parse_args()
    d0, d1 = dt.date.fromisoformat(a.tu), dt.date.fromisoformat(a.den)
    days = [d0 + dt.timedelta(i) for i in range((d1 - d0).days + 1)]
    if a.chi_quanh_su_co:
        from incidents import INCIDENTS
        keep = set()
        for r in INCIDENTS:
            if r[11] != "Sự cố": continue
            s0 = dt.date.fromisoformat(r[3]); keep |= {s0 + dt.timedelta(k) for k in range(-a.so_ngay, a.so_ngay)}
            if r[5]:
                e0 = dt.date.fromisoformat(r[5]); keep |= {e0 + dt.timedelta(k) for k in range(1, a.so_ngay + 1)}
        days = [x for x in days if x in keep]
        print("Số ngày quanh sự cố:", len(days))
    tasks = [(x, m) for x in days for m in MSMS if x >= dt.date.fromisoformat(MSMS[m][2])]
    print("Số yêu cầu:", len(tasks))
    rows, errs = [], []
    with ThreadPoolExecutor(a.luong) as ex:
        for i, res in enumerate(ex.map(lambda t: one(t[0], t[1], a.gio_utc), tasks)):
            for r in res:
                (errs if r and r[0] == "LOI" else rows).append(r)
            if i % 500 == 0: print(f"{i}/{len(tasks)}")
    rows.sort(key=lambda r: (r[0], r[1], r[4]))
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(COLS); w.writerows(rows)
    print("Đã ghi", a.out, len(rows), "dòng; lỗi:", len(errs))

if __name__ == "__main__":
    main()
