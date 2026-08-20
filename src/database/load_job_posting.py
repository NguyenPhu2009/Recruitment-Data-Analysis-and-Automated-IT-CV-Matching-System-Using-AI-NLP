import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import time
import os
from dotenv import load_dotenv

# Tải cấu hình từ file .env (An toàn khi đẩy lên GitHub và server)
load_dotenv()

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '200905')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_NAME = os.environ.get('DB_NAME', 'ats_db')

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Nối đường dẫn an toàn đa nền tảng (Bây giờ sẽ là Thư_mục_gốc/data/processed/clean_all_jobs.csv)
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'clean_all_jobs.csv')

try:
    print(f"--- ĐANG ĐỌC FILE: {input_file} ---")

    df = pd.read_csv(input_file, encoding='utf-8')

    column_mapping = {
        'job_id': 'job_id',
        'title': 'title',
        'company_name': 'company_name',
        'size': 'company_size',
        'location': 'location',
        'job_level': 'job_level',
        'exp_year': 'experience_year',
        'salary_min': 'salary_min',
        'salary_max': 'salary_max',
        'is_negotiable': 'is_negotiable',
        'job_type': 'job_type',
        'is_remote': 'is_remote',
        'posted_date': 'posted_date',
        'source': 'source',
        'crawled_at': 'crawled_at',
        'url': 'job_url',
        'desc': 'desc',
        'req': 'req'
    }
    df = df.rename(columns=column_mapping)
    columns_in_sql = list(column_mapping.values())
    df = df[[col for col in columns_in_sql if col in df.columns]]

    # ==============================================================
    # QUY TRÌNH XỬ LÝ DỮ LIỆU ĐÚNG THỨ TỰ CHO MYSQL
    # ==============================================================

    # BƯỚC 1: Ép kiểu dữ liệu an toàn (Biến các chuỗi lỗi thành NaN)
    if 'salary_min' in df.columns:
        df['salary_min'] = pd.to_numeric(df['salary_min'], errors='coerce')
    if 'salary_max' in df.columns:
        df['salary_max'] = pd.to_numeric(df['salary_max'], errors='coerce')

    # BƯỚC 2: Chuyển Boolean thành Integer (0 hoặc 1)
    if 'is_negotiable' in df.columns:
        df['is_negotiable'] = df['is_negotiable'].fillna(False).astype(int)
    if 'is_remote' in df.columns:
        df['is_remote'] = df['is_remote'].fillna(False).astype(int)

    # BƯỚC 3: Chuyển đổi định dạng Date sang YYYY-MM-DD
    if 'posted_date' in df.columns:
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
    if 'crawled_at' in df.columns:
        df['crawled_at'] = pd.to_datetime(df['crawled_at'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')

    # BƯỚC 4 (QUAN TRỌNG NHẤT): Xử lý Rỗng (NULL) ở khâu cuối cùng
    # Đảm bảo tất cả NaN sinh ra từ 3 bước trên đều được chuyển thành None (NULL trong SQL)
    df = df.replace({np.nan: None})
    df = df.where(pd.notnull(df), None)

    # ==============================================================

    print(f"\n--- ĐANG XÓA SẠCH DỮ LIỆU CŨ TẠI BẢNG Job_Postings ---")
    with engine.begin() as conn:
        # Tắt kiểm tra khóa ngoại tạm thời để xóa sạch dữ liệu (tránh lỗi nếu có FK từ bảng Job_Skill)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        conn.execute(text("TRUNCATE TABLE Job_Postings;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        print("-> Đã xóa dữ liệu cũ thành công.")

    print(f"\n--- ĐANG ĐẨY DỮ LIỆU MỚI VÀO BẢNG Job_Postings ---")
    start_time = time.time()

    df.to_sql(
        name='job_postings',
        con=engine,
        if_exists='append',
        index=False
    )

    end_time = time.time()
    print(f"🎉 Nạp thành công {len(df)} dòng dữ liệu chuẩn xác.")
    print(f"⏱️ Thời gian thực thi: {round(end_time - start_time, 2)} giây.")

except Exception as e:
    print(f"❌ [LỖI]: {e}")