from flask_restx import Namespace

auth_ns = Namespace('auth', description='Операции, связанные с аутентификацией')

from . import routes
