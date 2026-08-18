from app.models.database import db
from datetime import datetime

class CVMatchingHistory(db.Model):
    __tablename__ = 'CV_Matching_History'

    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'))

    job_title = db.Column(db.String(255), nullable=False)
    job_jd = db.Column(db.Text, nullable=True)

    cv_filename = db.Column(db.String(255))
    overall_score = db.Column(db.Float)
    skill_score = db.Column(db.Float)
    exp_score = db.Column(db.Float)
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)