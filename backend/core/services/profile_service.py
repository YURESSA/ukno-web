from backend.core.messages import AuthMessages
from backend.core.services.auth_service import *


def parse_user_data(data, default_role):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")
    role_name = data.get("role_name", default_role)
    return username, email, password, full_name, phone, role_name


def register_user(default_role, data, current_user_role="user"):
    username, email, password, full_name, phone, role_name = parse_user_data(data, default_role)

    if current_user_role != "admin":
        role_name = default_role

    new_user = create_user(username, email, password, full_name, phone, role_name)
    if not new_user:
        return {"message": AuthMessages.USER_ALREADY_EXISTS}, HTTPStatus.CONFLICT
    return {"message": AuthMessages.USER_CREATED}, HTTPStatus.CREATED


def login_user(role, data):
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password) or user.role.role_name.lower() != role.lower():
        return None
    return authenticate_user(username, password)


def get_profile():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    if not user:
        return None, {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
    return user, None, None


def change_profile_password(data):
    current_username = get_jwt_identity()
    if change_password(current_username, data.get("old_password"), data.get("new_password")):
        return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK
    return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST


def delete_profile():
    current_username = get_jwt_identity()
    if delete_user(current_username):
        return {"message": AuthMessages.USER_DELETED_SELF}, HTTPStatus.OK
    return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND


def get_user_info_response(user):
    if not user:
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.role_name
    }, HTTPStatus.OK


def update_user(username, data):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None

    # Проверка email на уникальность
    if 'email' in data and data['email'] != user.email:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            raise ValueError("Email уже используется другим пользователем")
        user.email = data['email']

    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    # Обновление роли по имени
    if 'role_name' in data:
        role_name = data['role_name']
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f"Роль '{role_name}' не найдена")
        user.role_id = role.role_id

    db.session.commit()
    return user

