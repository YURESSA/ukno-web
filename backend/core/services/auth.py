from flask_jwt_extended import create_access_token
from backend.core.services.user import get_user_by_username


def authenticate_user(username, password, required_role=None):
    user = get_user_by_username(username)
    if not user or not user.check_password(password):
        return None

    if required_role and user.role.role_name != required_role:
        return None

    return create_access_token(identity=user.username, additional_claims={"role": user.role.role_name})


def change_password(username, old_password, new_password):
    user = get_user_by_username(username)
    if user and user.check_password(old_password):
        user.set_password(new_password)
        from backend.core import db
        db.session.commit()
        return True
    return False
