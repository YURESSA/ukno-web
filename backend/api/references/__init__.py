from flask_restx import Namespace

ref_ns = Namespace('references', description='Справочные данные')

from . import ref_roles, ref_stats, ref_categories, ref_age_categories, ref_format_types  # noqa: F401, E402
