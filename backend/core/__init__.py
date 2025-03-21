from flask import Flask
from flask_cors import CORS

from .config import Config
from .database import db, migrate
from .extentions import swagger, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    swagger.init_app(app)
    jwt.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from backend.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
