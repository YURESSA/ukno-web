from flask_restx import fields

from backend.core import api

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль')
})

user_model = api.model('User', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'email': fields.String(required=True, description='Электронная почта'),
    'password': fields.String(required=True, description='Пароль'),
    'full_name': fields.String(required=True, description='Полное имя'),
    'phone': fields.String(required=True, description='Телефон'),
    'role_name': fields.String(required=False, description='Роль пользователя')
})

change_password_model = api.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Старый пароль'),
    'new_password': fields.String(required=True, description='Новый пароль')
})

username_model = api.model('Username', {
    'username': fields.String(required=True, description='Имя пользователя')
})

user_type_model = api.model('UserType', {
    'role': fields.String(required=True, description='Роль пользователя (например, admin, user, resident)')
})

edit_profile_model = api.model("EditProfile", {
    "full_name": fields.String(required=False, description="Полное имя"),
    "email": fields.String(required=False, description="Email"),
    "phone": fields.String(required=False, description="Номер телефона"),
})
