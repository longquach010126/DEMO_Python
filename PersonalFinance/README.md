# Quản lý Chi tiêu và Thu nhập Cá nhân (Personal Finance)

Dự án ứng dụng quản lý chi tiêu cá nhân viết bằng Python, Tkinter, SQLite, và Matplotlib.

## Cấu trúc dự án
- `main.py`: File chạy chính của chương trình.
- `database.py`: Xử lý kết nối và khởi tạo cơ sở dữ liệu SQLite.
- `models.py`: Chứa các model dữ liệu và logic truy vấn.
- `gui.py`: Chứa giao diện Tkinter chính.
- `data/`: Thư mục chứa file database `finance.db`.

## Cài đặt
1. Cài đặt Python 3 trên máy của bạn.
2. Cài đặt thư viện matplotlib để hiển thị biểu đồ:
   ```bash
   pip install matplotlib
   ```

## Chạy chương trình
Chạy lệnh sau trong Terminal:
```bash
python main.py
```

## Chức năng
- **Tổng quan:** Hiển thị tổng thu nhập, tổng chi tiêu, và số dư hiện tại.
- **Giao dịch:** Thêm, xóa, xem danh sách các khoản thu/chi.
- **Thống kê:** Xem thống kê chi tiêu theo danh mục (yêu cầu cài đặt matplotlib).
