# -*- coding: utf-8 -*-
"""
Làm sạch và ghép dữ liệu cho Chương 3:
  vào : ripe_raw.csv (dữ liệu ping RIPE Atlas theo ngày, từng probe x đích)
        incidents.py (bảng mốc thời gian sự cố)
  ra  : 02_ripe_atlas_ping_theo_ngay.csv   – dữ liệu sạch, có ISP và nhóm đích
        04_ripe_theo_ngay_theo_isp.csv     – trung vị giữa các probe, theo ngày x ISP x nhóm đích
        05_so_tuyen_dang_su_co_theo_ngay.csv
        06_so_sanh_truoc_trong_sau.csv     – bảng nghiên cứu sự kiện (event study)
"""
import sys, os, datetime as dt
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from incidents import INCIDENTS, COLUMNS, ASSUMED_END

RAW, OUT = sys.argv[1], sys.argv[2]
PROBE = pd.read_csv(os.path.join(OUT, "03_probe_ripe_atlas.csv"))
MSM = {
    1001: ("k.root-servers.net", "root"), 1004: ("f.root-servers.net", "root"),
    1011: ("c.root-servers.net", "root"),
    18854725: ("sg-sin-as55002 anchor", "Singapore"), 23871798: ("sg-sin-as16276 anchor", "Singapore"),
    29781560: ("sg-sin-as12008 anchor", "Singapore"), 40447822: ("sg-sin-as38001 anchor", "Singapore"),
    25787843: ("us-lax-as3491 anchor", "Mỹ (Los Angeles)"), 26070042: ("tw-tpe-as3491 anchor", "Đông Bắc Á"),
    25313148: ("kr-sel-as20473 anchor", "Đông Bắc Á"), 63883300: ("hk-hkg-as32167 anchor", "Hong Kong"),
}
cols = ["ngay", "probe_id", "msm_id", "dst_addr", "so_lan_do", "goi_gui", "goi_nhan", "mat_goi_pct",
        "rtt_min_ms", "rtt_trungvi_ms", "rtt_p95_ms", "jitter_ms"]
d = pd.read_csv(RAW, header=None, names=cols) if open(RAW, encoding="utf-8-sig").read(4) != "ngay" \
    else pd.read_csv(RAW, encoding="utf-8-sig")
d = d[cols]
d = d[d["msm_id"].isin(MSM)].drop_duplicates(["ngay", "probe_id", "msm_id"])
d = d.merge(PROBE[["probe_id", "isp", "asn"]], on="probe_id", how="left")
d["dich"] = d["msm_id"].map(lambda m: MSM[m][0])
d["nhom_dich"] = d["msm_id"].map(lambda m: MSM[m][1])
# Root DNS là anycast: phân loại theo RTT tối thiểu trong ngày
root = d["nhom_dich"] == "root"
d.loc[root & (d["rtt_min_ms"] < 10), "nhom_dich"] = "Root DNS – bản sao trong nước (đối chứng)"
d.loc[root & ~(d["rtt_min_ms"] < 10), "nhom_dich"] = "Root DNS – bản sao nước ngoài"
d = d[d["goi_gui"] > 0]
# Quy tắc làm sạch: ngày mà đích mất từ 50% gói trở lên coi là "đích không phản hồi"
# (bị chặn ICMP, lỗi định tuyến tới đích...). Giữ tỉ lệ mất gói, nhưng bỏ RTT và jitter của
# ngày đó, vì RTT tính từ vài gói lọt qua không đại diện.
MAT_GOI_NGUONG = 50
d["rtt_hop_le"] = d["mat_goi_pct"] < MAT_GOI_NGUONG
for c in ("rtt_min_ms", "rtt_trungvi_ms", "rtt_p95_ms", "jitter_ms"):
    d.loc[~d["rtt_hop_le"], c] = None
print("so ngay-cap bi loai RTT do mat goi >= 50%:", int((~d["rtt_hop_le"]).sum()))
d = d.sort_values(["ngay", "isp", "probe_id", "msm_id"])
order = ["ngay", "isp", "asn", "probe_id", "msm_id", "dich", "nhom_dich", "dst_addr", "so_lan_do", "goi_gui",
         "goi_nhan", "mat_goi_pct", "rtt_min_ms", "rtt_trungvi_ms", "rtt_p95_ms", "jitter_ms", "rtt_hop_le"]
d[order].to_csv(os.path.join(OUT, "02_ripe_atlas_ping_theo_ngay.csv"), index=False, encoding="utf-8-sig")

# Trung vị giữa các probe theo ngày x ISP x nhóm đích
agg = (d.groupby(["ngay", "isp", "nhom_dich"])
         .agg(so_probe=("probe_id", "nunique"), rtt_trungvi_ms=("rtt_trungvi_ms", "median"),
              rtt_p95_ms=("rtt_p95_ms", "median"), jitter_ms=("jitter_ms", "median"),
              mat_goi_pct=("mat_goi_pct", "mean"))
         .round(2).reset_index())
agg.to_csv(os.path.join(OUT, "04_ripe_theo_ngay_theo_isp.csv"), index=False, encoding="utf-8-sig")

# Số tuyến đang sự cố mỗi ngày (chỉ tính sự cố có ngày khôi phục đã biết)
inc = pd.DataFrame(INCIDENTS, columns=COLUMNS)
ev = inc[inc["Loại sự kiện"] == "Sự cố"].copy()
days = pd.date_range("2022-01-01", "2025-12-31")
ev["ket_thuc_tinh"] = ev["Ngày khôi phục"]
for k, (v, _) in ASSUMED_END.items():
    ev.loc[ev["ID"] == k, "ket_thuc_tinh"] = v
ev_known = ev[ev["Ngày khôi phục"] != ""]
ev_assm = ev[ev["ket_thuc_tinh"] != ""]
def active(tab, col, day):
    return tab[(pd.to_datetime(tab["Ngày sự cố"]) <= day) & (pd.to_datetime(tab[col]) >= day)]
rows5 = []
for day in days:
    a1 = active(ev_known, "Ngày khôi phục", day); a2 = active(ev_assm, "ket_thuc_tinh", day)
    rows5.append({"ngay": day.date(), "so_tuyen_su_co_ngay_khoi_phuc_da_biet": a1["Tuyến cáp"].nunique(),
                  "so_tuyen_su_co_co_gia_dinh": a2["Tuyến cáp"].nunique(),
                  "cac_tuyen_dang_su_co": "|".join(sorted(a2["Tuyến cáp"].unique())),
                  "ma_su_co": "|".join(sorted(a2["ID"]))})
pd.DataFrame(rows5).to_csv(os.path.join(OUT, "05_so_tuyen_dang_su_co_theo_ngay.csv"), index=False, encoding="utf-8-sig")

# Bảng so sánh trước / trong / sau – tính theo TỪNG CẶP ĐO CỐ ĐỊNH (probe x đích)
# Lý do: nếu gộp nhiều probe rồi so sánh, việc một probe ngừng hoạt động hoặc bắt đầu
# hoạt động sẽ làm trung vị nhảy vọt dù mạng không đổi (sai lệch do thay đổi thành phần mẫu).
d["ngay"] = pd.to_datetime(d["ngay"])
METRICS = ("rtt_trungvi_ms", "jitter_ms", "mat_goi_pct")
pair_rows = []
for _, e in ev.iterrows():
    if e["Độ chính xác ngày sự cố"] != "ngày": continue
    s = pd.Timestamp(e["Ngày sự cố"])
    if not (pd.Timestamp("2022-01-15") <= s <= pd.Timestamp("2025-12-31")): continue
    end = pd.Timestamp(e["Ngày khôi phục"]) if e["Ngày khôi phục"] else None
    win = {"truoc": (s - pd.Timedelta(days=14), s - pd.Timedelta(days=1)),
           "trong": (s, s + pd.Timedelta(days=13))}
    if end is not None and e["Độ chính xác ngày khôi phục"] in ("ngày", "tháng"):
        win["sau"] = (end + pd.Timedelta(days=1), end + pd.Timedelta(days=14))
    sub = d[(d["ngay"] >= win["truoc"][0]) & (d["ngay"] <= max(b for a, b in win.values()))]
    for (p, m), g in sub.groupby(["probe_id", "msm_id"]):
        r = {"id": e["ID"], "tuyen": e["Tuyến cáp"], "ngay_su_co": e["Ngày sự cố"],
             "ngay_khoi_phuc": e["Ngày khôi phục"], "isp": g["isp"].iloc[0], "probe_id": p,
             "msm_id": m, "dich": g["dich"].iloc[0]}
        for k, (a, b) in win.items():
            w = g[(g["ngay"] >= a) & (g["ngay"] <= b)]
            r[f"so_ngay_{k}"] = int(w["rtt_trungvi_ms"].notna().sum())
            if k == "truoc" and len(w): r["nhom_dich"] = w["nhom_dich"].mode().iloc[0]
            for mt in METRICS:
                r[f"{mt}_{k}"] = round(w[mt].median(), 2) if len(w) else None
        if r.get("so_ngay_truoc", 0) < 7 or r.get("so_ngay_trong", 0) < 7: continue
        for mt in METRICS:
            a, b = r.get(f"{mt}_truoc"), r.get(f"{mt}_trong")
            r[f"thay_doi_{mt}_pct"] = round(100 * (b - a) / a, 1) if a and a > 0 and b is not None else None
        pair_rows.append(r)
pr = pd.DataFrame(pair_rows)
first = ["id", "tuyen", "ngay_su_co", "ngay_khoi_phuc", "isp", "probe_id", "msm_id", "dich", "nhom_dich"]
pr = pr[first + [c for c in pr.columns if c not in first]]
pr.to_csv(os.path.join(OUT, "06_so_sanh_truoc_trong_sau.csv"), index=False, encoding="utf-8-sig")

# Tóm tắt theo sự cố x ISP (chỉ đích ở nước ngoài, bỏ nhóm đối chứng)
q = pr[~pr["nhom_dich"].str.contains("trong nước", na=False)]
summ = (q.groupby(["id", "tuyen", "ngay_su_co", "isp"])
          .agg(so_cap_do=("probe_id", "size"),
               so_cap_anchor=("nhom_dich", lambda v: int((~v.str.startswith("Root")).sum())),
               trungvi_thay_doi_rtt_pct=("thay_doi_rtt_trungvi_ms_pct", "median"),
               so_cap_rtt_tang_tren_10pct=("thay_doi_rtt_trungvi_ms_pct", lambda v: int((v > 10).sum())),
               trungvi_thay_doi_jitter_pct=("thay_doi_jitter_ms_pct", "median"),
               mat_goi_truoc_pct=("mat_goi_pct_truoc", "mean"),
               mat_goi_trong_pct=("mat_goi_pct_trong", "mean"))
          .round(2).reset_index())
anc = (q[~q["nhom_dich"].str.startswith("Root")].groupby(["id", "isp"])["thay_doi_rtt_trungvi_ms_pct"]
         .median().round(2).rename("trungvi_thay_doi_rtt_pct_chi_anchor").reset_index())
summ = summ.merge(anc, on=["id", "isp"], how="left")
cols = list(summ.columns); cols.insert(cols.index("so_cap_rtt_tang_tren_10pct"), cols.pop(cols.index("trungvi_thay_doi_rtt_pct_chi_anchor")))
summ = summ[cols]
summ.to_csv(os.path.join(OUT, "06b_tom_tat_su_co_theo_isp.csv"), index=False, encoding="utf-8-sig")
print("rows raw", len(d), "agg", len(agg), "pair rows", len(pr), "summary rows", len(summ))
