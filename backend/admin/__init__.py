from flask_restx import Namespace

admin_ns = Namespace('admin', description='Эндпоинты для администратора')

from . import routes  # noqa: F401, E402
