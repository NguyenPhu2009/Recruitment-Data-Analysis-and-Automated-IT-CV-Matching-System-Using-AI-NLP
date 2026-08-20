from flask import current_app
from ..models.database import db
from ..models.job_posting import JobPosting
from ..models.cv_matching_history import CVMatchingHistory


class DatabaseConnector:

    def __init__(self):
        # Giữ nguyên để không ảnh hưởng đến các hàm khởi tạo khác nếu có gọi engine
        self.engine = db.engine

    def get_connection(self):
        # Trả về db.session chuẩn của Flask-SQLAlchemy (Đã tự động quản lý Pool & Thread-safe)
        return db.session

    def fetch_job_by_id(self, job_id: int) -> JobPosting:
        try:
            # Sử dụng session scoped an toàn trên Production
            return db.session.get(JobPosting, job_id)
        except Exception as e:
            print(f"[Error] Lỗi khi lấy thông tin Job {job_id}: {str(e)}")
            return None

    def save_matching_record(self, history: CVMatchingHistory) -> bool:
        try:
            # Đảm bảo luồng dữ liệu luôn được cô lập và an toàn tuyệt đối
            db.session.add(history)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"[Error] Không thể lưu lịch sử matching: {str(e)}")
            return False