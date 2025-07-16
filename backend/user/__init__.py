from flask_restx import Namespace

from . import routes  # noqa: F401

user_ns = Namespace('user', description='Эндпоинты для обычного пользователя')
