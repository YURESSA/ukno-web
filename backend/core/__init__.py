from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db, migrate
from .extensions import jwt, api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    api.init_app(app)
    jwt.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    register_apps(app)

    return app


def register_apps(app):
    from backend.auth import auth_ns
    api.add_namespace(auth_ns, path='/auth')
    from backend.app_example import new_app_ns
    api.add_namespace(new_app_ns, path='/app_example')
