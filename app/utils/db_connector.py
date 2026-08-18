from flask import current_app
from ..models.database import db
from ..models.job_posting import JobPosting
from ..models.cv_matching_history import CVMatchingHistory


class DatabaseConnector:

    def __init__(self):
        self.engine = db.engine

    def get_connection(self):
        return db.session

    def fetch_job_by_id(self, job_id: int) -> JobPosting:
        return JobPosting.query.get(job_id)

    def save_matching_record(self, history: CVMatchingHistory) -> bool:
        try:
            session = self.get_connection()
            session.add(history)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f"[Error] Không thể lưu lịch sử matching: {str(e)}")
            return False