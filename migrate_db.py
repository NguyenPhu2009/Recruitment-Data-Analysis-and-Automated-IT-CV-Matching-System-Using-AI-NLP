import pandas as pd
from sqlalchemy import create_engine, event
import pyodbc
import urllib.parse

server = r'NGUYENANPHU\MAYAO'
database = 'ATS_Database'

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
)
sql_server_conn = f"mssql+pyodbc:///?odbc_connect={params}"

mysql_conn = "mysql+pymysql://root:200905@localhost:3306/ats_db"

engine_sql = create_engine(sql_server_conn)
engine_mysql = create_engine(mysql_conn)

@event.listens_for(engine_sql, 'connect')
def receive_connect(dbapi_connection, connection_record):
    dbapi_connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16le')
    dbapi_connection.setdecoding(pyodbc.SQL_CHAR, encoding='windows-1258')
    dbapi_connection.setencoding(encoding='utf-16le')

tables = [
    "Job_Postings",
    "Skills_Dict",
    "Job_Skill",
    "Users",
    "CV_Matching_History"
]

print("🚀 Bắt đầu quá trình Migration từ SQL Server sang MySQL...\n")

for table in tables:
    print(f"Đang chuyển bảng: {table}...")
    try:
        df = pd.read_sql_table(table, con=engine_sql)

        df.to_sql(name=table, con=engine_mysql, if_exists='replace', index=False)
        print(f"-> Hoàn tất chuyển {len(df)} dòng!\n")
    except Exception as e:
        print(f"-> ❌ Lỗi ở bảng {table}: {e}\n")

print("✅ Đã hoàn tất quá trình Migration!")