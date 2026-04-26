from flask_restx import Namespace

yandex_ns = Namespace('yandex', description='Операции с Яндекс Картами')

from . import routes  # noqa: F401, E402
