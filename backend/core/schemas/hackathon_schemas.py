from flask_restx import fields

from backend.core import api

hackathon_case_model = api.model('HackathonCase', {
    'title': fields.String(required=True, description="Название кейса хакатона"),
    'description': fields.String(required=True, description="Описание кейса хакатона"),
    'file': fields.String(description="Загрузите файл с подробным ТЗ (PDF или DOCX)", required=True),
})
