import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ats_super_secret_key_2026'

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:200905@localhost:3306/ats_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False