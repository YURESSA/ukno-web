from flask_restx import Namespace

from . import routes  # noqa: F401

resident_ns = Namespace('resident', description='Эндпоинты для резидента')
