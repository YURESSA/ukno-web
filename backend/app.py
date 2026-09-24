import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import redirect, send_from_directory, render_template
from sqlalchemy import inspect, text

from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.event_models import Category, AgeCategory, FormatType
from backend.core.scripts.clear_unpaid import cleanup_unpaid_reservations
from backend.core.scripts.create_superuser import create_superuser
from backend.core.scripts.ensure_data import ensure_data_exists
from backend.core.storage import file_url, uses_s3


def seed_reference_data():
    ensure_data_exists(db, Category, 'categories.json', 'category_id', 'category_name')
    ensure_data_exists(db, AgeCategory, 'age_categories.json', 'age_category_id', 'age_category_name')
    ensure_data_exists(db, FormatType, 'format_types.json', 'format_type_id', 'format_type_name')


def init_database():
    # Import all model modules before create_all so SQLAlchemy registers every table.
    from backend.core.models import auth_models, event_models, merch_models, news_models, ref_models  # noqa: F401

    db.create_all()

    # Keep existing local SQLite databases usable when optional content fields
    # are added. create_all() creates missing tables but never adds columns to
    # tables that already exist.
    inspector = inspect(db.engine)
    compatibility_columns = {
        "news": (("short_description", "VARCHAR(300)"),),
        "users": (("role", "VARCHAR(8)"),),
        "events": (
            ("short_description", "VARCHAR(512)"),
            ("latitude", "FLOAT"),
            ("longitude", "FLOAT"),
        ),
    }
    for table_name, required_columns in compatibility_columns.items():
        if not inspector.has_table(table_name):
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name, column_type in required_columns:
            if column_name not in existing_columns:
                db.session.execute(text(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                ))

    if inspector.has_table("users"):
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "role_id" in user_columns:
            if inspector.has_table("roles"):
                db.session.execute(text("""
                    UPDATE users
                    SET role = COALESCE(
                        (SELECT LOWER(roles.role_name) FROM roles WHERE roles.role_id = users.role_id),
                        'user'
                    )
                    WHERE role IS NULL OR role = ''
                """))
            else:
                db.session.execute(text("""
                    UPDATE users
                    SET role = CASE role_id
                        WHEN 1 THEN 'admin'
                        WHEN 2 THEN 'resident'
                        ELSE 'user'
                    END
                    WHERE role IS NULL OR role = ''
                """))
    db.session.commit()

    # create_all() does not change existing columns. Production historically
    # had users.phone as VARCHAR(15), while the UI submits formatted numbers
    # longer than that. Keep old installations compatible on every startup.
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(text('ALTER TABLE users ALTER COLUMN phone TYPE VARCHAR(32)'))
        db.session.commit()


def register_static_routes(app):
    upload_folder_abs = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER)

    @app.route('/media/uploads/<path:filename>')
    def uploaded_file(filename):
        if uses_s3():
            return redirect(file_url(filename))
        if Config.PRODUCTION:
            return send_from_directory('/app/media/uploads', filename)
        else:
            return send_from_directory(str(upload_folder_abs), filename)

    @app.route('/admin-panel/', strict_slashes=False)
    def admin_page():
        return render_template('admin/admin_panel.html', title="Админ-панель")

    @app.route('/login-admin/', strict_slashes=False)
    def login_page():
        return render_template('login.html', title="Вход в систему")


def run_cleanup(app):
    with app.app_context():
        try:
            count = cleanup_unpaid_reservations()
            app.logger.info(f"Очистка неоплаченных броней выполнена, удалено {count}")
        except Exception as e:
            app.logger.exception("Ошибка при очистке броней: %s", e)


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

        elif cmd == "init_db":
            with app.app_context():
                init_database()
            print("Database schema initialized.")
            sys.exit(0)

        elif cmd == "clear_unpaid_reservations":
            with app.app_context():
                cleanup_unpaid_reservations()
            sys.exit(0)

    register_static_routes(app)

    app.run(debug=True, use_reloader=True)


if __name__ == '__main__':
    main()
