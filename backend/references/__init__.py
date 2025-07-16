from flask_restx import Namespace

from . import routes  # noqa: F401

ref_ns = Namespace('references', description='Справочные данные')
