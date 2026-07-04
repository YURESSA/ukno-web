import os

from dotenv import load_dotenv
from yookassa import Configuration

load_dotenv()


def str_to_bool(value):
    if value is None:
        return False
    return value.lower() in ("true", "1", "t", "yes", "y")


class Config:
    if os.path.basename(os.getcwd()) == "backend":
        PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
    else:
        PROJECT_ROOT = os.path.abspath(os.getcwd())

    TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'backend', 'templates')
    STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'backend', 'static')
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 * 7 * 4
    JWT_TOKEN_LOCATION = ["headers"]

    if str_to_bool(os.getenv("USE_POSTGRES")):
        POSTGRES_USER = os.getenv("POSTGRES_USER", "ukno_user")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ukno_pass")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "ukno")
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLITE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_ORIGINS = ["*"]

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "media/uploads")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif").split(',')
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))
    MAX_FORM_MEMORY_SIZE = int(os.getenv("MAX_FORM_MEMORY_SIZE", 5 * 1024 * 1024))
    MAX_FORM_PARTS = int(os.getenv("MAX_FORM_PARTS", 200))
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_DEBUG = str_to_bool(os.getenv("MAIL_DEBUG", "False"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    Configuration.account_id = os.environ.get("ACCOUNT_ID")
    Configuration.secret_key = os.environ.get("YOOKASSA_SECRET_KEY")
    YOOKASSA_REDIRECT_URI = os.environ.get("YOOKASSA_REDIRECT_URI")
    YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")

    PRODUCTION = str_to_bool(os.getenv("PRODUCTION", "False"))
