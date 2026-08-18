from .database import db
from sqlalchemy import NVARCHAR, UnicodeText

class JobPosting(db.Model):
    __tablename__ = 'Job_Postings'

    job_id = db.Column(db.Integer, primary_key=True)

    title = db.Column(NVARCHAR(255))
    company_name = db.Column(NVARCHAR(255))
    company_size = db.Column(NVARCHAR(100), nullable=True)
    location = db.Column(NVARCHAR(255))
    job_level = db.Column(NVARCHAR(100))
    experience_year = db.Column(NVARCHAR(100))

    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    is_negotiable = db.Column(db.Boolean)

    job_type = db.Column(NVARCHAR(100))
    is_remote = db.Column(db.Boolean)
    posted_date = db.Column(db.Date)
    source = db.Column(NVARCHAR(100))
    crawled_at = db.Column(db.Date)

    job_url = db.Column(db.Text)

    desc = db.Column('desc', UnicodeText)
    req = db.Column('req', UnicodeText)

    skills = db.relationship('SkillsDict', secondary='Job_Skill', lazy='subquery',
                             backref=db.backref('jobs', lazy=True))

    def __repr__(self):
        return f"<Job {self.job_id} - {self.title}>"