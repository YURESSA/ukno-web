from flask_restx import Namespace

user_ns = Namespace('user', description='Эндпоинты для обычного пользователя')

from . import user_auth, user_excursions, user_news, user_reservations, user_profile  # noqa: F401, E402
