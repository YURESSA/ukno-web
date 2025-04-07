from backend.core import db
from backend.core.models.models import User, Role


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_role_by_name(role_name):
    return Role.query.filter_by(role_name=role_name).first()


def get_all_users(role=None):
    query = User.query

    if role:
        query = query.filter(User.role.has(role_name=role))

    users = query.all()
    return users


def create_user(username, email, password, full_name, phone, role_name="Пользователь"):
    role = get_role_by_name(role_name)
    if not role or User.query.filter((User.username == username) | (User.email == email)).first():
        return None

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        phone=phone,
        role_id=role.role_id
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return new_user


def delete_user(username):
    user = get_user_by_username(username)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False
