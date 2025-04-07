from flask_restx import Namespace

resident_ns = Namespace('resident', description='Эндпоинты для резидента')

from . import routes
