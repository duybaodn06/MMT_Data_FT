# Minh chứng thu thập dữ liệu: Sự cố cáp quang biển và chất lượng truy cập Internet tại Việt Nam (2022–2025)

Thư mục này là minh chứng phần **thu thập và tiền xử lý dữ liệu** cho đồ án nhóm môn **Mạng máy tính**: *Phân tích mối liên hệ giữa sự cố cáp quang biển và chất lượng truy cập Internet tại Việt Nam giai đoạn 2022–2025*.

Người thực hiện: Nguyễn Duy Bảo, phụ trách Dữ liệu và Thu thập số liệu.

Toàn bộ dữ liệu đo được lấy bằng mã nguồn trong thư mục `scripts/`, qua **REST API công khai của RIPE Atlas** và **bộ dữ liệu mở M-Lab NDT**; bảng mốc sự cố được tổng hợp thủ công từ báo chí, mỗi sự cố ghi rõ nguồn. Chạy lại một lệnh là tái tạo được toàn bộ dữ liệu trong `du_lieu/`.

## Dữ liệu đã thu thập

| Nguồn | Cách lấy | Phạm vi | Kết quả |
|---|---|---|---|
| RIPE Atlas | REST API `atlas.ripe.net/api/v2/measurements/{id}/results/`, script `lay_du_lieu_ripe_atlas.py` | 1/1/2022–31/12/2025, mỗi ngày khung 20:00–21:00 giờ Việt Nam; 18 thiết bị đo của VNPT, FPT, Viettel; 11 phép đo ping (3 máy chủ DNS gốc k/f/c-root và 8 phép đo tới máy chủ neo ở Singapore, Hong Kong, Đài Bắc, Seoul, Los Angeles) | 36.163 bản ghi thô (`ripe_raw.csv`), sau làm sạch còn 35.591 bản ghi theo ngày |
| M-Lab NDT | Tệp thống kê theo tháng (IQB) công khai, script `lay_du_lieu_mlab.py` | 1/2022–12/2025; cả nước và 3 mạng VNPT (AS45899), Viettel (AS7552), FPT (AS18403) | 192 dòng (48 tháng × 4 đối tượng) |
| Báo chí | Tổng hợp thủ công, lưu trong `scripts/incidents.py` | 2022–2025 | 26 sự cố, 3 sự kiện hạ tầng mới, 2 sự cố sau giai đoạn nghiên cứu (31 dòng), mỗi dòng có link nguồn |

Danh sách thiết bị đo: `du_lieu/03_probe_ripe_atlas.csv`. Mã các phép đo (measurement ID): biến `MSMS` trong `scripts/lay_du_lieu_ripe_atlas.py`. Mô tả các nguồn: `du_lieu/00_nguon_du_lieu.csv`.

## Cấu trúc thư mục

```
.
├── README.md                 ← file này
├── requirements.txt          ← thư viện Python cần cài
├── chay_tat_ca.py            ← chạy toàn bộ quy trình bằng 1 lệnh
├── docs/
│   └── MO_TA_DU_LIEU.md      ← mô tả chi tiết từng file và từng cột dữ liệu
├── scripts/
│   ├── incidents.py              ← bảng mốc thời gian sự cố, kèm nguồn báo chí
│   ├── build_timeline.py         ← xuất bảng sự cố ra CSV
│   ├── lay_du_lieu_ripe_atlas.py ← gọi API RIPE Atlas, tổng hợp ping theo ngày
│   ├── lay_du_lieu_mlab.py       ← tải thống kê M-Lab theo tháng
│   ├── xu_ly_du_lieu.py          ← làm sạch, so sánh trước/trong/sau sự cố
│   └── build_excel.py            ← gom kết quả vào 1 file Excel
└── du_lieu/                  ← dữ liệu đã thu thập và kết quả xử lý
    ├── ripe_raw.csv          ← dữ liệu thô tải từ RIPE Atlas
    ├── 00_nguon_du_lieu.csv … 07_mlab_vn_theo_thang.csv
    └── DuLieu_CapQuangBien_2022_2025.xlsx
```

## Cài đặt và chạy

Yêu cầu Python 3.9 trở lên.

```bash
pip install -r requirements.txt
python chay_tat_ca.py
```

| Lệnh | Việc làm | Thời gian |
|---|---|---|
| `python chay_tat_ca.py` | Tải RIPE Atlas mọi ngày 2022–2025, tải M-Lab, xử lý, xuất Excel | 70–90 phút |
| `python chay_tat_ca.py --nhanh` | Chỉ tải RIPE Atlas 7 ngày quanh mỗi sự cố | 15–25 phút |
| `python chay_tat_ca.py --bo-ripe` | Dùng lại `du_lieu/ripe_raw.csv` đã có, không tải lại RIPE Atlas | ~10 phút |
| `python chay_tat_ca.py --bo-ripe --bo-mlab` | Chỉ xử lý lại từ dữ liệu đã có | ~1 phút |

Lấy riêng một giai đoạn, ví dụ đợt sự cố tháng 2/2023:

```bash
python scripts/lay_du_lieu_ripe_atlas.py --tu 2023-02-15 --den 2023-02-28 --out thu.csv
```

Thêm `--gio-utc 20` để đo khung giờ thấp điểm (03:00 giờ Việt Nam) thay cho giờ cao điểm 20:00.

## Dữ liệu đầu ra

| File | Nội dung | Số dòng |
|---|---|---|
| `01_moc_thoi_gian_su_co.csv` | 26 sự cố, 3 sự kiện hạ tầng mới, kèm nguồn báo chí | 31 |
| `02_ripe_atlas_ping_theo_ngay.csv` | RTT, jitter, mất gói theo ngày của từng cặp thiết bị – đích | 35.591 |
| `03_probe_ripe_atlas.csv` | Thiết bị đo RIPE Atlas tại Việt Nam | 18 |
| `04_ripe_theo_ngay_theo_isp.csv` | Gộp theo ngày × nhà mạng (chỉ để xem tổng quan) | 9.513 |
| `05_so_tuyen_dang_su_co_theo_ngay.csv` | Số tuyến cáp đang lỗi mỗi ngày | 1.461 |
| `06_so_sanh_truoc_trong_sau.csv` | So sánh trước/trong/sau theo từng cặp đo | 346 |
| `06b_tom_tat_su_co_theo_isp.csv` | Tóm tắt theo sự cố × nhà mạng | 36 |
| `07_mlab_vn_theo_thang.csv` | M-Lab: tốc độ tải, độ trễ, mất gói theo tháng | 192 |
| `DuLieu_CapQuangBien_2022_2025.xlsx` | Tất cả các bảng trên, kèm sheet hướng dẫn | 10 sheet |

Giải thích từng cột: xem [`docs/MO_TA_DU_LIEU.md`](docs/MO_TA_DU_LIEU.md).

## Phương pháp

- **Nghiên cứu theo sự kiện (event study):** So sánh 14 ngày trước sự cố, 14 ngày đầu sự cố và 14 ngày sau khi khôi phục.
- **Đơn vị so sánh là cặp đo cố định** (một thiết bị đo → một máy chủ đích), không gộp cả nhà mạng, để tránh số liệu nhảy vọt khi thiết bị đo bật/tắt.
- **Đích đo:** Máy chủ neo (anchor) RIPE Atlas có vị trí cố định ở Singapore, Hong Kong, Đài Bắc, Seoul, Los Angeles; máy chủ DNS gốc k/f/c-root. DNS gốc có RTT tối thiểu dưới 10 ms được xếp vào **nhóm đối chứng trong nước** (không đi qua cáp biển).
- **Làm sạch:** Bỏ bản ghi trùng và bản ghi không gửi được gói nào. Ngày mất từ 50% gói trở lên được giữ tỷ lệ mất gói nhưng bỏ RTT và jitter.
- **Chỉ số:** RTT trung vị là chỉ số chính; jitter và mất gói là chỉ số phụ; tốc độ tải M-Lab dùng để kiểm chứng.

## Hạn chế

- Mỗi nhà mạng chỉ có 1–5 thiết bị RIPE Atlas cùng lúc, chủ yếu ở TP.HCM và Hà Nội.
- Viettel chỉ có thiết bị RIPE Atlas từ 6/2024 và chỉ đo tới DNS gốc.
- Mỗi ngày chỉ lấy 1 giờ cao điểm (20:00–21:00 giờ Việt Nam).
- Ngày sự cố lấy từ báo chí; một số chỉ chính xác đến tháng. Nhiều sự cố chồng lấn nhau.
- Số bài đo M-Lab tăng mạnh từ giữa 2024, nên chỉ so sánh các tháng gần nhau.

## Nguồn dữ liệu và trích dẫn

- RIPE NCC. (2026). *RIPE Atlas measurement data* [Data set]. https://atlas.ripe.net
- Measurement Lab. (2026). *NDT monthly statistics (IQB)* [Data set]. https://github.com/m-lab/iqb
- RIPE NCC Staff. (2015). RIPE Atlas: A global Internet measurement network. *The Internet Protocol Journal, 18*(3).
- Dovrolis, C., Gummadi, K., Kuzmanovic, A., & Meinrath, S. D. (2010). Measurement Lab: Overview and an invitation to the research community. *ACM SIGCOMM Computer Communication Review, 40*(3), 53–56. https://doi.org/10.1145/1823844.1823853
- Nguồn báo chí cho từng sự cố: cột `Nguồn 1`, `Nguồn 2` trong `du_lieu/01_moc_thoi_gian_su_co.csv`.

Dữ liệu đo thuộc về RIPE NCC và M-Lab, được dùng theo điều khoản của từng nguồn; khi dùng lại, vui lòng trích dẫn như trên.
