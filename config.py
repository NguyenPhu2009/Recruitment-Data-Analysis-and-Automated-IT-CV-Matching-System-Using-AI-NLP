import os
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env vào hệ thống
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ats_super_secret_key_2026'

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Lấy thông tin kết nối từ file .env.
    # Tham số thứ 2 là giá trị mặc định (Fallback) dùng cho môi trường Local nếu không tìm thấy biến môi trường.
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '200905')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'ats_db')

    # Tổ hợp chuỗi kết nối an toàn
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    SQLALCHEMY_TRACK_MODIFICATIONS = False