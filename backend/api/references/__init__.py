from flask_restx import Namespace

ref_ns = Namespace('references', description='Справочные данные')

from . import (ref_roles, ref_stats, ref_categories, ref_age_categories,  # noqa: F401, E402
               ref_format_types, ref_projects, ref_trust_reason, ref_company_history, ref_team,  # noqa: F401, E402
               ref_cultural_space)  # noqa: F401, E402
