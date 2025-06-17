import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    def str_to_bool(value):
        return value.lower() in ("true", "1", "t", "yes", "y")
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')
    STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 * 7 * 4
    JWT_TOKEN_LOCATION = ["headers"]

    if str_to_bool(os.getenv("USE_POSTGRESS")):
        SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRES_URL", "sqlite:///db.sqlite3")
    else:
        POSTGRES_USER = os.getenv("POSTGRES_USER", "ukno_user")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ukno_pass")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "ukno")
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
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



    PRODUCTION = str_to_bool(os.getenv("PRODUCTION", "False"))
