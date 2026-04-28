from flask_restx import Namespace

resident_ns = Namespace('resident', description='Эндпоинты для резидента')

from . import (resident_auth, resident_analytics,  # noqa: F401, E402
               resident_sessions, resident_excursions, resident_photos)  # noqa: F401, E402
