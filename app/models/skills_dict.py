from .database import db
from sqlalchemy import NVARCHAR

job_skill = db.Table('Job_Skill',
                     db.Column('job_id', db.Integer, db.ForeignKey('Job_Postings.job_id', ondelete="CASCADE"),
                               primary_key=True),
                     db.Column('skill_id', db.Integer, db.ForeignKey('Skills_Dict.skill_id', ondelete="CASCADE"),
                               primary_key=True)
                     )


class SkillsDict(db.Model):
    __tablename__ = 'Skills_Dict'

    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(NVARCHAR(255), nullable=False)
    skill_category = db.Column(NVARCHAR(255))
    normalized_form = db.Column(NVARCHAR(255))

    def __repr__(self):
        return f"<Skill {self.skill_name}>"