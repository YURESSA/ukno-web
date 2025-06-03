from http import HTTPStatus

from flask_jwt_extended import create_access_token, get_jwt_identity

from backend.core import db
from backend.core.models.auth_models import User, Role


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


def create_user(username, email, password, full_name, phone, role_name):
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

def update_profile(data):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    new_email = data.get("email")
    new_phone = data.get("phone")
    new_full_name = data.get("full_name")


    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return {"message": "Этот email уже используется"}, HTTPStatus.BAD_REQUEST
        user.email = new_email

    if new_phone:
        user.phone = new_phone

    if new_full_name:
        user.full_name = new_full_name

    db.session.commit()

    return {"message": "Профиль обновлён успешно"}, HTTPStatus.OK

def change_profile_password(data):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return {"message": "Оба поля обязательны"}, HTTPStatus.BAD_REQUEST

    if not user.check_password(old_password):
        return {"message": "Неверный текущий пароль"}, HTTPStatus.UNAUTHORIZED

    user.set_password(new_password)
    db.session.commit()

    return {"message": "Пароль успешно изменён"}, HTTPStatus.OK
