import pandas as pd
from sqlalchemy import create_engine, text
import time
import os

# ==========================================
# CẤU HÌNH KẾT NỐI MYSQL
# ==========================================
DB_USER = 'root'       # Thay bằng username MySQL của bạn
DB_PASSWORD = '200905'       # Thay bằng password MySQL của bạn (nếu có)
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ats_db'

# Tạo chuỗi kết nối MySQL (Sử dụng pymysql)
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

job_skill_file = r"../../data/processed/Job_Skill.csv"

try:
    print("--- ĐANG ĐỌC DỮ LIỆU ---")

    # Ép chuẩn utf-8 khi đọc file
    job_skill_df = pd.read_csv(job_skill_file, encoding='utf-8')

    # Ép kiểu dữ liệu sang số nguyên (INT) để khớp tuyệt đối với CSDL
    job_skill_df['job_id'] = job_skill_df['job_id'].astype(int)
    job_skill_df['skill_id'] = job_skill_df['skill_id'].astype(int)

    print(f"-> Mapping Kỹ năng - Job: {len(job_skill_df)} dòng.")

    with engine.begin() as conn:
        # Tắt kiểm tra khóa ngoại tạm thời để xóa sạch dữ liệu
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        conn.execute(text("TRUNCATE TABLE Job_Skill;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    print("\n-> Đã dọn sạch dữ liệu cũ trong Database.")

    # ==========================================
    # 4. NẠP DỮ LIỆU MỚI
    # ==========================================
    print("\n--- ĐANG ĐẨY DỮ LIỆU VÀO MYSQL ---")
    start_time = time.time()

    # 4.2. Nạp bảng con: Job_Skill
    job_skill_df.to_sql(
        name='job_skill',
        con=engine,
        if_exists='append',
        index=False
    )
    print("✅ Đã nạp xong bảng Job_Skill.")

    end_time = time.time()
    print(f"\n🎉 [HOÀN TẤT] Nạp thành công toàn bộ dữ liệu Kỹ năng.")
    print(f"⏱️ Thời gian thực thi: {round(end_time - start_time, 2)} giây.")

except Exception as e:
    print(f"❌ [LỖI HỆ THỐNG]: {e}")