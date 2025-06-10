from backend.app import register_static_routes
from backend.core import create_app

app = create_app()
register_static_routes(app)
