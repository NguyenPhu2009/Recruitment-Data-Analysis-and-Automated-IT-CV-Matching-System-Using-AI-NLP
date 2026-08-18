import pandas as pd
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

job_skill_file = r"../../data/processed/Job_Skill.csv"

try:
    print("--- ĐANG ĐỌC DỮ LIỆU ---")

    # [ĐÃ UPDATE]: Ép chuẩn utf-8 khi đọc fi
    job_skill_df = pd.read_csv(job_skill_file, encoding='utf-8')

    # Ép kiểu dữ liệu sang số nguyên (INT) để khớp tuyệt đối với CSDL
    job_skill_df['job_id'] = job_skill_df['job_id'].astype(int)
    job_skill_df['skill_id'] = job_skill_df['skill_id'].astype(int)

    print(f"-> Mapping Kỹ năng - Job: {len(job_skill_df)} dòng.")


    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Job_Skill;"))
    print("\n-> Đã dọn sạch dữ liệu cũ trong Database.")

    # ==========================================
    # 4. NẠP DỮ LIỆU MỚI
    # ==========================================
    print("\n--- ĐANG ĐẨY DỮ LIỆU VÀO SQL SERVER ---")
    start_time = time.time()


    # 4.2. Nạp bảng con: Job_Skill
    job_skill_df.to_sql(
        name='Job_Skill',
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