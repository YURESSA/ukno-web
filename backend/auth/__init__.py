from flask_restx import Namespace

auth_ns = Namespace('auth', description='Authentication related operations')

from . import routes
