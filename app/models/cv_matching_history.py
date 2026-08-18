from .database import db
from datetime import datetime
from sqlalchemy import NVARCHAR, UnicodeText, DateTime, Integer, Float, String, Text


class CVMatchingHistory(db.Model):
    # Tên bảng trong MySQL (lưu ý viết thường nếu MySQL của bạn phân biệt hoa/thường)
    __tablename__ = 'cv_matching_history'

    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Khóa ngoại trỏ tới bảng user (Lưu ý: Đảm bảo bảng User của bạn có __tablename__ là 'users' hoặc 'Users' tương ứng)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # ---------------------------------------------------------
    # ĐÃ XÓA: job_id
    # ĐÃ THÊM: 2 Cột mới để lưu chức danh và nội dung JD
    job_title = db.Column(db.String(255), default="Vị trí tùy chỉnh")
    job_jd = db.Column(db.Text)
    # ---------------------------------------------------------

    cv_filename = db.Column(NVARCHAR(255))

    overall_score = db.Column(db.Float)
    skill_score = db.Column(db.Float)
    exp_score = db.Column(db.Float)

    matched_skills = db.Column(UnicodeText)
    missing_skills = db.Column(UnicodeText)

    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HistoryResult {self.result_id}: {self.overall_score}%>"