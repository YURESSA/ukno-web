from flask_restx import Namespace

user_ns = Namespace('user', description='Эндпоинты для обычного пользователя')

from . import routes  # noqa: F401, E402
