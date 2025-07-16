from flask_restx import Namespace

from . import routes  # noqa: F401

admin_ns = Namespace('admin', description='Эндпоинты для администратора')
