from flask_restx import Namespace

webhook_ns = Namespace('webhook', description='Эндпоинты для администратора')

from . import routes  # noqa: F401, E402
