from flask_restx import Namespace

jury_ns = Namespace('jury', description='Эндпоинты для члена жюри')

from . import routes
