# 1. Mục đích

- Bộ dữ liệu phục vụ Chương 3 của đồ án "Phân tích mối liên hệ giữa sự cố cáp quang biển và chất lượng truy cập Internet tại Việt Nam giai đoạn 2022–2025".
- Thiết kế nghiên cứu: nghiên cứu theo sự kiện (event study), so sánh chất lượng mạng trước / trong / sau từng sự cố, tách theo nhà mạng: VNPT (AS45899), Viettel (AS7552), FPT (AS18403).

# 2. Các file trong thư mục du_lieu

- ripe_raw.csv: Dữ liệu ping RIPE Atlas thô, chưa làm sạch. Giữ lại để xử lý lại mà không phải tải lại.
- 00_nguon_du_lieu.csv: Bảng các nguồn dữ liệu và cách lấy.
- 01_moc_thoi_gian_su_co.csv: Mốc thời gian sự cố cáp biển 2022–2025 và sự kiện hạ tầng mới; mỗi dòng có 1–2 nguồn báo chí.
- 02_ripe_atlas_ping_theo_ngay.csv: Dữ liệu ping đã làm sạch, 1 dòng = 1 ngày x 1 thiết bị đo x 1 đích đo. Dùng để vẽ biểu đồ theo ngày.
- 03_probe_ripe_atlas.csv: Danh sách thiết bị đo RIPE Atlas tại Việt Nam (nhà mạng, vị trí, thời gian hoạt động).
- 04_ripe_theo_ngay_theo_isp.csv: Trung vị giữa các thiết bị, theo ngày x nhà mạng x nhóm đích. CHÚ Ý: số thiết bị (cột so_probe) thay đổi theo thời gian nên giá trị có thể nhảy vọt khi một thiết bị bật/tắt. Chỉ dùng để xem tổng quan, không dùng để so sánh.
- 05_so_tuyen_dang_su_co_theo_ngay.csv: Số tuyến cáp đang sự cố mỗi ngày, tính từ file 01.
- 06_so_sanh_truoc_trong_sau.csv: So sánh trước / trong / sau theo từng cặp đo cố định (thiết bị x đích).
- 06b_tom_tat_su_co_theo_isp.csv: Tóm tắt file 06 theo sự cố x nhà mạng (đã bỏ nhóm đối chứng trong nước).
- 07_mlab_vn_theo_thang.csv: Thống kê M-Lab NDT theo tháng cho cả nước và từng nhà mạng.
- DuLieu_CapQuangBien_2022_2025.xlsx: Tất cả các bảng trên trong một file Excel.

# 3. Cách đo của RIPE Atlas (file 02, 04, 06, 06b)

- Nguồn: RIPE Atlas (RIPE NCC), API công khai atlas.ripe.net. Thiết bị đo (probe) do tình nguyện viên đặt trong mạng của nhà mạng.
- Lấy mẫu: mỗi ngày 1 giờ cao điểm 20:00–21:00 giờ Việt Nam; ping 3 gói mỗi 4 phút, tức khoảng 15 lần đo (45 gói) cho mỗi thiết bị, mỗi đích, mỗi ngày.
- Đích đo cố định ở nước ngoài (máy chủ neo, anchor): Singapore (4 máy), Hong Kong, Đài Bắc và Seoul (nhóm Đông Bắc Á), Los Angeles (Mỹ). Vị trí đích cố định nên độ trễ tăng phản ánh việc lưu lượng phải đi đường vòng.
- DNS gốc (k-root, f-root, c-root) là anycast: nếu RTT tối thiểu trong ngày dưới 10 ms thì xếp vào nhóm "bản sao trong nước (đối chứng)", đường đi không qua cáp biển; còn lại xếp nhóm "bản sao nước ngoài".
- Quy tắc làm sạch: bỏ bản ghi trùng; bỏ bản ghi không gửi được gói nào; ngày mất từ 50% gói trở lên thì giữ tỷ lệ mất gói nhưng bỏ RTT và jitter (cột rtt_hop_le = False).

# 4. Các cột của file 02 (và sheet RIPE_theo_cap_do)

- ngay: Ngày đo (khung 20:00–21:00 giờ Việt Nam).
- isp, asn: Nhà mạng và số hiệu mạng.
- probe_id: Mã thiết bị đo RIPE Atlas.
- msm_id: Mã phép đo RIPE Atlas.
- dich, dst_addr: Tên và địa chỉ IP của máy chủ đích.
- nhom_dich: Singapore, Hong Kong, Đông Bắc Á, Mỹ (Los Angeles), Root DNS – bản sao nước ngoài, Root DNS – bản sao trong nước (đối chứng).
- so_lan_do: Số lần ping trong giờ đo (thường 15).
- goi_gui, goi_nhan: Số gói tin gửi đi và nhận về.
- mat_goi_pct: Tỷ lệ mất gói, %.
- rtt_min_ms, rtt_trungvi_ms, rtt_p95_ms: Độ trễ khứ hồi nhỏ nhất, trung vị, phân vị 95, ms.
- jitter_ms: Trung bình chênh lệch tuyệt đối giữa 2 RTT liên tiếp, ms (theo ý tưởng RFC 3550).
- rtt_hop_le: True nếu ngày đó mất dưới 50% gói, RTT được dùng để phân tích.

# 5. Các cột của file 04 (sheet RIPE_ngay_ISP)

- ngay, isp, nhom_dich: Như file 02.
- so_probe: Số thiết bị đo có dữ liệu trong ngày.
- rtt_trungvi_ms, rtt_p95_ms, jitter_ms: Trung vị giữa các thiết bị, ms.
- mat_goi_pct: Trung bình tỷ lệ mất gói giữa các thiết bị, %.

# 6. Các cột của file 06 (sheet Truoc_Trong_Sau_CapDo)

- id, tuyen, ngay_su_co, ngay_khoi_phuc: Mã sự cố, tuyến cáp, ngày lỗi, ngày khôi phục (khớp file 01).
- isp, probe_id, msm_id, dich, nhom_dich: Cặp đo cố định.
- so_ngay_truoc, so_ngay_trong, so_ngay_sau: Số ngày có RTT hợp lệ trong mỗi cửa sổ 14 ngày. Chỉ giữ cặp có ít nhất 7 ngày ở cửa sổ trước và trong.
- rtt_trungvi_ms_truoc / _trong / _sau: Trung vị RTT theo ngày trong mỗi cửa sổ, ms.
- jitter_ms_truoc / _trong / _sau, mat_goi_pct_truoc / _trong / _sau: Tương tự cho jitter (ms) và mất gói (%).
- thay_doi_rtt_trungvi_ms_pct, thay_doi_jitter_ms_pct, thay_doi_mat_goi_pct_pct: % thay đổi giữa cửa sổ trong và cửa sổ trước.

# 7. Các cột của file 06b (sheet TomTat_SuCo_ISP)

- id, tuyen, ngay_su_co, isp: Sự cố và nhà mạng.
- so_cap_do: Số cặp đo tới đích nước ngoài đủ dữ liệu.
- so_cap_anchor: Trong đó, số cặp tới máy chủ neo có vị trí cố định.
- trungvi_thay_doi_rtt_pct: Trung vị % thay đổi RTT trên mọi cặp đo nước ngoài.
- trungvi_thay_doi_rtt_pct_chi_anchor: Trung vị % thay đổi RTT chỉ trên máy chủ neo. Đáng tin hơn vì đích không đổi vị trí.
- so_cap_rtt_tang_tren_10pct: Số cặp đo có RTT tăng quá 10%.
- trungvi_thay_doi_jitter_pct: Trung vị % thay đổi jitter.
- mat_goi_truoc_pct, mat_goi_trong_pct: Tỷ lệ mất gói trung bình trước và trong sự cố, %.

# 8. Các cột của file 07 (sheet MLab_theo_thang)

- thang: Tháng (YYYY-MM).
- chieu: tai_xuong.
- doi_tuong: Cả nước, VNPT, Viettel hoặc FPT.
- sample_count: Số bài đo trong tháng.
- download_pN: Phân vị N của tốc độ tải xuống, Mbit/s (p50 là trung vị).
- latency_pN, loss_pN: Phân vị "theo chất lượng": p1 là nhóm 1% kém nhất, p99 là tốt nhất, p50 vẫn là trung vị. latency tính bằng ms, loss là tỷ lệ 0–1.

# 9. Hạn chế

- Viettel chỉ có thiết bị RIPE Atlas từ giữa 2024, nên so sánh đủ 3 nhà mạng chỉ làm được cho sự cố từ 6/2024.
- Mỗi nhà mạng chỉ có 1–5 thiết bị cùng lúc, chủ yếu ở TP.HCM và Hà Nội; không đại diện cho toàn bộ thuê bao.
- Mỗi ngày chỉ lấy 1 giờ cao điểm; chạy lại script với --gio-utc 20 để lấy giờ thấp điểm (03:00 giờ Việt Nam).
- Ngày sự cố lấy từ báo chí; ngày có độ chính xác "tháng" là ước tính. Nhiều sự cố chồng lấn nên khó tách riêng tác động của từng tuyến.
- Ping (ICMP) có thể bị thiết bị mạng ưu tiên thấp; độ trễ ping không phản ánh tốc độ tải.
- Số bài đo M-Lab tăng mạnh từ giữa 2024, nên chỉ so sánh các tháng gần nhau.

# 10. Trích dẫn nguồn (APA)

- RIPE NCC. (2026). RIPE Atlas measurement data [Data set]. https://atlas.ripe.net
- Measurement Lab. (2026). NDT monthly statistics (IQB) [Data set]. https://github.com/m-lab/iqb
- Báo chí: xem cột Nguồn 1, Nguồn 2 trong file 01.
