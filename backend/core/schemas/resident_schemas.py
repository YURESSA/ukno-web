from flask_restx import fields

from backend.api.resident import resident_ns

resident_login = resident_ns.model('ResidentLogin', {
    'email': fields.String(required=True, description='Электронная почта резидента', example='resident@example.com'),
    'password': fields.String(required=True, description='Пароль резидента', example='resident123')
})
