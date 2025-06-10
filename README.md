
# 🏥 Hệ Thống Đăng Ký Khám Bệnh - Flask Web App

## 📌 Mô tả
Đây là một ứng dụng web xây dựng bằng **Flask** nhằm phục vụ nhu cầu **đăng ký khám bệnh trực tuyến**, quản lý cuộc hẹn giữa **bệnh nhân** và **bác sĩ**. Hệ thống bao gồm các chức năng chính như:
- Đăng ký và quản lý tài khoản bệnh nhân
- Đặt lịch hẹn khám với bác sĩ
- Xác nhận, hủy hoặc cập nhật trạng thái cuộc hẹn
- Trang quản trị dành cho admin theo dõi, lọc và xử lý lịch khám
---
## 🛠️ Công nghệ sử dụng

- Frontend: HTML, CSS, JS, BOOTSTRAP 5, Jinja2, ....
- Backend: Python, FLASK, ...
- Database: Flask-SQLAlchemy, SQLite 

---



## 🔑 Tính năng chính

### 👤 Bệnh nhân
- Đăng ký / Đăng nhập
- Tạo và xem lịch hẹn
- Hủy lịch hẹn

### 👨‍⚕️ Admin
- Xem danh sách lịch hẹn
- Lọc theo trạng thái (Pending, Confirmed, Cancelled)
- Xác nhận hoặc hủy lịch
- Xem thông tin bệnh nhân & bác sĩ liên quan
---


## ⚙️ Cách chạy ứng dụng

### 1. Clone project
```bash
git clone https://github.com/yourusername/healthcare-flask-app.git
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Hoặc venv\Scripts\activate trên Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình CSDL (nếu dùng SQLite)
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Chạy app
```bash
set FLASK_APP=app.py
set FLASK_ENV=development
Python app.py 
```

---
## 📄 License
MIT License © 2025
