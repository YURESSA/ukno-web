from flask_restx import Namespace

from . import routes  # noqa: F401

webhook_ns = Namespace('webhook', description='Эндпоинты для администратора')
