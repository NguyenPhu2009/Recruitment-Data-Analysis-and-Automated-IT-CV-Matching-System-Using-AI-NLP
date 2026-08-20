import pandas as pd
from sqlalchemy import create_engine, text
import time
import os
from dotenv import load_dotenv

# Tải cấu hình từ file .env
load_dotenv()

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '200905')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_NAME = os.environ.get('DB_NAME', 'ats_db')

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

# SỬA ĐƯỜNG DẪN TUYỆT ĐỐI AN TOÀN CHO LINUX
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dict_file = os.path.join(BASE_DIR, 'data', 'processed', 'Skills_Dict.csv')

try:
    print(f"--- ĐANG ĐỌC FILE: {dict_file} ---")
    skills_df = pd.read_csv(dict_file, encoding='utf-8')
    skills_df['skill_id'] = skills_df['skill_id'].astype(int)

    print(f"-> Từ điển Kỹ năng: {len(skills_df)} dòng.")

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        conn.execute(text("TRUNCATE TABLE Skills_Dict;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    print("-> Đã dọn sạch dữ liệu cũ trong Database.")

    print("\n--- ĐANG ĐẨY DỮ LIỆU VÀO MYSQL ---")  # SỬA LOG CHỮ TỪ SQL SERVER -> MYSQL
    start_time = time.time()
    skills_df.to_sql(name='skills_dict', con=engine, if_exists='append', index=False)
    end_time = time.time()

    print(f"🎉 Nạp thành công {len(skills_df)} dòng từ điển kỹ năng.")
    print(f"⏱️ Thời gian thực thi: {round(end_time - start_time, 2)} giây.")

except Exception as e:
    print(f"❌ [LỖI]: {e}")