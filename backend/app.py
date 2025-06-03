import os
import sys

from flask import send_from_directory, render_template  # импорт render_template добавлен

from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import Role
from backend.core.models.excursion_models import Category, AgeCategory, FormatType
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
        return send_from_directory(str(upload_folder_abs), filename)

    @app.route('/admin/', strict_slashes=False)
    def admin_page():
        return render_template('admin/admin_panel.html', title="Админ-панель")
    @app.route('/login/', strict_slashes=False)
    def login_page():
        return render_template('login.html', title="Вход в систему")


def main():
    app = create_app()

    if len(sys.argv) > 1 and sys.argv[1] == "create_superuser":
        with app.app_context():
            create_superuser()
        sys.exit(0)

    register_static_routes(app)
    with app.app_context():
        seed_reference_data()

    app.run(debug=True, use_reloader=True)


if __name__ == '__main__':
    main()
