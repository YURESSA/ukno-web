from flask_restx import fields
from backend.core import api

# Модель входа — заменили username на email
login_model = api.model('Login', {
    'email': fields.String(required=True, description='Электронная почта'),
    'password': fields.String(required=True, description='Пароль')
})

# Модель пользователя — убрали username
user_model = api.model('User', {
    'email': fields.String(required=True, description='Электронная почта'),
    'password': fields.String(required=True, description='Пароль'),
    'full_name': fields.String(required=True, description='Полное имя'),
    'phone': fields.String(required=True, description='Телефон'),
    'role_name': fields.String(required=False, description='Роль пользователя')
})

# Модель смены пароля
change_password_model = api.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Старый пароль'),
    'new_password': fields.String(required=True, description='Новый пароль')
})


# Модель фильтрации по типу пользователя
user_type_model = api.model('UserType', {
    'role': fields.String(required=True, description='Роль пользователя (например, admin, user, resident)')
})

# Модель редактирования профиля
edit_profile_model = api.model("EditProfile", {
    "full_name": fields.String(required=False, description="Полное имя"),
    "email": fields.String(required=False, description="Электронная почта"),
    "phone": fields.String(required=False, description="Телефон"),
})
