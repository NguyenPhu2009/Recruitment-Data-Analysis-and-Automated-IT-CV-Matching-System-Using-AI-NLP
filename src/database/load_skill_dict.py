import pandas as pd
from sqlalchemy import create_engine, text
import urllib
import time

DB_USER = 'root'       # Thay bằng username MySQL của bạn
DB_PASSWORD = '200905'       # Thay bằng password MySQL của bạn (nếu có)
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ats_db'

# Tạo chuỗi kết nối MySQL (Sử dụng pymysql)
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

dict_file = r"../../data/processed/Skills_Dict.csv"

try:
    print("--- ĐANG ĐỌC DỮ LIỆU ---")

    # [ĐÃ UPDATE]: Ép chuẩn utf-8 khi đọc file
    skills_df = pd.read_csv(dict_file, encoding='utf-8')

    # Ép kiểu dữ liệu sang số nguyên (INT) để khớp tuyệt đối với CSDL
    skills_df['skill_id'] = skills_df['skill_id'].astype(int)

    print(f"-> Từ điển Kỹ năng: {len(skills_df)} dòng.")

    # Xóa bảng Job_Skill trước, Skills_Dict sau để không vi phạm ràng buộc khóa ngoại
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Job_Skill;"))
    print("\n-> Đã dọn sạch dữ liệu cũ trong Database.")

    # ==========================================
    # 4. NẠP DỮ LIỆU MỚI
    # ==========================================
    print("\n--- ĐANG ĐẨY DỮ LIỆU VÀO SQL SERVER ---")
    start_time = time.time()

    # 4.1. Nạp bảng cha: Skills_Dict
    skills_df.to_sql(
        name='skills_dict',
        con=engine,
        if_exists='append',
        index=False
    )
    print("✅ Đã nạp xong bảng Skills_Dict.")


    end_time = time.time()
    print(f"\n🎉 [HOÀN TẤT] Nạp thành công toàn bộ dữ liệu Kỹ năng.")
    print(f"⏱️ Thời gian thực thi: {round(end_time - start_time, 2)} giây.")

except Exception as e:
    print(f"❌ [LỖI HỆ THỐNG]: {e}")