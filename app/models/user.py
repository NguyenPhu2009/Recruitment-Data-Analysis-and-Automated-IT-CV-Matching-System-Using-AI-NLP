from .database import db
from datetime import datetime
from sqlalchemy import NVARCHAR, VARCHAR, DateTime

class User(db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(VARCHAR(255), unique=True, nullable=False)
    password_hash = db.Column(VARCHAR(255), nullable=False)
    full_name = db.Column(NVARCHAR(255), nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"