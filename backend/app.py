import os
from flask import send_from_directory

from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import Role
from backend.core.models.excursion_models import Category
from backend.core.scripts.categories_initializer import ensure_categories_exist
from backend.core.scripts.create_session_from_recurring import create_sessions_from_recurring
from backend.core.scripts.role_initializer import ensure_roles_exist

if __name__ == '__main__':
    app = create_app()
    upload_folder_abs = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER)

    @app.route('/media/uploads/<path:filename>')
    def uploaded_file(filename):
        print(upload_folder_abs)
        return send_from_directory(app.config['MEDIA_FOLDER'], filename)

    with app.app_context():
        ensure_roles_exist(db, Role)
        create_sessions_from_recurring()
        ensure_categories_exist(db, Category)

    app.run(debug=True, use_reloader=True)
