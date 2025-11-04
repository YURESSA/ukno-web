from flask_restx import fields

from backend.api.user import user_ns

user_login = user_ns.model('UserLogin', {
    'email': fields.String(required=True, description='Электронная почта пользователя', example='user@example.com'),
    'password': fields.String(required=True, description='Пароль пользователя', example='mypassword123')

})
