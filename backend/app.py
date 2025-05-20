from backend.core import create_app, db
from backend.core.models.auth_models import Role
from backend.core.scripts.create_session_from_recurring import create_sessions_from_recurring
from backend.core.scripts.role_initializer import ensure_roles_exist

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ensure_roles_exist(db, Role)
        create_sessions_from_recurring()
    app.run(debug=True, use_reloader=True)
