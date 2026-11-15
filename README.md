# 🎡 Hệ Thống Điểm Danh & Quản Lý Nhân Sự - KIDS PARK

Ứng dụng Web hỗ trợ điểm danh nhân viên bằng nhận diện khuôn mặt và quản lý lịch phân ca tuần theo thời gian thực, tương thích trên cả máy tính và điện thoại di động.

## 🚀 Công nghệ sử dụng
* **Ngôn ngữ:** Python
* **Giao diện Web:** Streamlit
* **Xử lý ảnh & Nhận diện khuôn mặt:** OpenCV (`Haar Cascade`)
* **Cơ sở dữ liệu:** MySQL
* **Xuất báo cáo:** Pandas, OpenPyXL (`.xlsx`)

## ✨ Chức năng chính
* **Quản lý (`Quan_ly`):**
  * Thêm tài khoản nhân viên mới (không yêu cầu chụp ảnh trước).
  * Phân ca làm việc theo ma trận tuần trực quan (`A`, `C`, `T`, `AC`, `AT`, `OFF`).
  * Theo dõi lịch sử check-in toàn hệ thống và trích xuất bảng công tháng ra file Excel (`.xlsx`).
* **Nhân viên (`Nhan_vien`):**
  * Tự động chụp ảnh đăng ký khuôn mặt mẫu kết hợp điểm danh trong lần đầu tiên.
  * Điểm danh trực tiếp qua camera điện thoại hoặc webcam máy tính.
  * Xem lịch làm việc cá nhân theo tuần và tra cứu lịch sử điểm danh.

## ⚙️ Hướng dẫn cài đặt & Chạy thử
1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
Import file kids_park_db.sql vào MySQL và cập nhật thông tin kết nối trong file config.py.

Khởi chạy ứng dụng:

Bash
python -m streamlit run app_streamlit.py
🔐 Tài khoản trải nghiệm mặc định
Quản lý: Mã QL01 | Mật khẩu 123456

Nhân viên: Mã NV02 | Mật khẩu 123456
