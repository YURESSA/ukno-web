import os

from flask import Flask
from flask_cors import CORS

from .config import Config
from .database import db, migrate
from .extensions import jwt, api, mail


def create_app(testing=False):
    app = Flask(__name__, template_folder=Config.TEMPLATE_FOLDER, static_folder=Config.STATIC_FOLDER)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    app.config['MEDIA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'uploads')
    api.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    register_apps(app)
    if testing:
        app.config["TESTING"] = True
        app.config["JWT_SECRET_KEY"] = "test-secret"
    return app


def register_apps(app):
    from backend.api.user import user_ns
    api.add_namespace(user_ns, path='/api/user')

    from backend.api.admin import admin_ns
    api.add_namespace(admin_ns, path='/api/admin')

    from backend.api.resident import resident_ns
    api.add_namespace(resident_ns, path='/api/resident')

    from backend.api.references import ref_ns
    api.add_namespace(ref_ns, path='/api/references')

    from backend.api.webhook import webhook_ns
    api.add_namespace(webhook_ns, path='/api/webhook')

    from backend.api.login import login_ns
    api.add_namespace(login_ns, path='/api')
