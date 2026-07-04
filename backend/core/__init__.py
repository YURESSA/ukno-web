import logging
import os
from time import time

import flask
from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

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

    app.logger.setLevel(logging.INFO)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)

        if not any(isinstance(h, logging.FileHandler) for h in app.logger.handlers):
            app.logger.addHandler(file_handler)

        app.logger.info("Приложение Flask создано и расширения инициализированы")

    @app.before_request
    def start_timer():
        flask.g.start_time = time()

    @app.after_request
    def log_request_info(response):
        duration = round((time() - flask.g.start_time) * 1000, 2)

        if response.status_code >= 400:
            app.logger.error(
                f"{flask.request.remote_addr} {flask.request.method} {flask.request.path} "
                f"{response.status_code} {duration}ms "
                f"UA:{flask.request.headers.get('User-Agent')}"
            )

        return response

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(e):
        return {
            "message": "Uploaded form data is too large",
            "max_content_length": app.config.get("MAX_CONTENT_LENGTH"),
            "max_form_memory_size": app.config.get("MAX_FORM_MEMORY_SIZE"),
        }, 413

    @app.errorhandler(Exception)
    def handle_exception(e):
        duration = round((time() - flask.g.start_time) * 1000, 2)

        app.logger.exception(
            f"UNHANDLED ERROR: {flask.request.remote_addr} {flask.request.method} {flask.request.path} "
            f"{duration}ms UA:{flask.request.headers.get('User-Agent')}"
        )

        return {"message": "Internal server error"}, 500

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

    from backend.api.frontend_logs import frontend_logs_ns
    api.add_namespace(frontend_logs_ns, path='/api/frontend-logs')

    from backend.api.yandex import yandex_ns
    api.add_namespace(yandex_ns, path='/api/yandex')
