from flask_restx import Namespace

ref_ns = Namespace('references', description='Справочные данные')

from . import routes
