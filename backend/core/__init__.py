import os

from flask import Flask
from flask_cors import CORS

from .config import Config
from .database import db, migrate
from .extensions import jwt, api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    app.config['MEDIA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'uploads')
    api.init_app(app)
    jwt.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    register_apps(app)

    return app


def register_apps(app):
    from backend.user import user_ns
    api.add_namespace(user_ns, path='/api/user')

    from backend.admin import admin_ns
    api.add_namespace(admin_ns, path='/api/admin')

    from backend.resident import resident_ns
    api.add_namespace(resident_ns, path='/api/resident')
