import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_TOKEN_LOCATION = ["headers"]

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_ORIGINS = ["*"]
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/uploads")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif").split(',')
