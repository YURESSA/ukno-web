import os

from dotenv import load_dotenv

load_dotenv()




class Config:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')
    STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 * 7 * 4
    JWT_TOKEN_LOCATION = ["headers"]

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_ORIGINS = ["*"]

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "media/uploads")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif").split(',')
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

