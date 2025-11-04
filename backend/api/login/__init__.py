from flask_restx import Namespace

login_ns = Namespace('resident', description='Универсальный логин для всех пользователей')

from . import routes  # noqa: F401, E402
