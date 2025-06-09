from flask_restx import Namespace

organizer_ns = Namespace('organizer', description='Эндпоинты для организатора')

from . import routes
