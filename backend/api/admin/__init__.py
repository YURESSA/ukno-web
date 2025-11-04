from flask_restx import Namespace

admin_ns = Namespace('admin', description='Эндпоинты для администратора')

from . import admin_auth, admin_news, admin_users, admin_excursions, admin_reservations  # noqa: F401, E402
