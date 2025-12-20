from flask_restx import Namespace

frontend_logs_ns = Namespace(
    'frontend-logs',
    description='Логирование ошибок с фронтенда'
)

from . import frontend_logs  # noqa: F401, E402
