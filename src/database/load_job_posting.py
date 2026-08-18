import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import urllib
import time

SERVER_NAME = r'NGUYENANPHU\MAYAO'
DATABASE_NAME = 'ATS_Database'

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

input_file = r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\data\processed\clean_all_jobs.csv"

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

    # Xử lý Rỗng (NULL)
    df = df.replace({np.nan: None})

    # Ép kiểu dữ liệu an toàn
    if 'salary_min' in df.columns:
        df['salary_min'] = pd.to_numeric(df['salary_min'], errors='coerce')
    if 'salary_max' in df.columns:
        df['salary_max'] = pd.to_numeric(df['salary_max'], errors='coerce')

    # --- [ĐIỂM SỬA CHỮA QUAN TRỌNG] ---

    # 1. Chuyển Boolean thành Integer (0 hoặc 1) cho khớp kiểu BIT
    if 'is_negotiable' in df.columns:
        df['is_negotiable'] = df['is_negotiable'].fillna(False).astype(int)
    if 'is_remote' in df.columns:
        df['is_remote'] = df['is_remote'].fillna(False).astype(int)

    # 2. Chuyển đổi định dạng Date sang YYYY-MM-DD cho khớp kiểu DATE
    if 'posted_date' in df.columns:
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
    if 'crawled_at' in df.columns:
        df['crawled_at'] = pd.to_datetime(df['crawled_at'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')


    print(f"\n--- ĐANG XÓA SẠCH DỮ LIỆU CŨ TẠI BẢNG Job_Postings ---")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Job_Postings;"))
        print("-> Đã xóa dữ liệu cũ thành công (Bảo toàn được Khóa ngoại).")

    print(f"\n--- ĐANG ĐẨY DỮ LIỆU MỚI VÀO BẢNG Job_Postings ---")
    start_time = time.time()

    df.to_sql(
        name='Job_Postings',
        con=engine,
        if_exists='append',
        index=False
    )

    end_time = time.time()
    print(f"🎉 Nạp thành công {len(df)} dòng dữ liệu chuẩn xác.")
    print(f"⏱️ Thời gian thực thi: {round(end_time - start_time, 2)} giây.")

except Exception as e:
    print(f"❌ [LỖI]: {e}")