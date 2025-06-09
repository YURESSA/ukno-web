from flask_restx import fields

from backend.core import api

team_model = api.model('Team', {
    'team_name': fields.String(required=True, description='Название команды'),
    'description': fields.String(required=False, description='Описание команды'),
})

team_invite_model = api.model('TeamInvite', {
    'team_name': fields.String(required=True, description='Название команды'),
    'username': fields.String(required=True, description='Имя пользователя для приглашения'),
})