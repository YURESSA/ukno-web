import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import send_from_directory, render_template

from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import Role
from backend.core.models.excursion_models import Category, AgeCategory, FormatType
from backend.core.scripts.clear_unpaid import cleanup_unpaid_reservations
from backend.core.scripts.create_superuser import create_superuser
from backend.core.scripts.ensure_data import ensure_data_exists


def seed_reference_data():
    ensure_data_exists(db, Role, 'roles.json', 'role_id', 'role_name')
    ensure_data_exists(db, Category, 'categories.json', 'category_id', 'category_name')
    ensure_data_exists(db, AgeCategory, 'age_categories.json', 'age_category_id', 'age_category_name')
    ensure_data_exists(db, FormatType, 'format_types.json', 'format_type_id', 'format_type_name')


def register_static_routes(app):
    upload_folder_abs = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER)

    @app.route('/media/uploads/<path:filename>')
    def uploaded_file(filename):
        if Config.PRODUCTION:
            return send_from_directory('/app/media/uploads', filename)
        else:
            return send_from_directory(str(upload_folder_abs), filename)

    @app.route('/admin-panel/', strict_slashes=False)
    def admin_page():
        return render_template('admin/admin_panel.html', title="Админ-панель")

    @app.route('/login/', strict_slashes=False)
    def login_page():
        return render_template('login.html', title="Вход в систему")


def run_cleanup(app):
    with app.app_context():
        cleanup_unpaid_reservations()


def main():
    app = create_app()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: run_cleanup(app), trigger="interval", minutes=5, )
    scheduler.start()

    import atexit
    atexit.register(lambda: scheduler.shutdown())

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "create_superuser":
            with app.app_context():
                create_superuser()
            sys.exit(0)

        elif cmd == "seed_reference_data":
            with app.app_context():
                seed_reference_data()
            print("Данные успешно посеяны.")
            sys.exit(0)

        elif cmd == "clear_unpaid_reservations":
            with app.app_context():
                cleanup_unpaid_reservations()
            sys.exit(0)

    register_static_routes(app)

    app.run(debug=True, use_reloader=True)


if __name__ == '__main__':
    main()
