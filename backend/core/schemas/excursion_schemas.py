from flask_restx import fields

from backend.core import api

excursion_model = api.model('ExcursionData', {
    'title': fields.String(required=True, description='Название экскурсии'),
    'description': fields.String(required=True, description='Описание экскурсии'),
    'duration': fields.Integer(required=True, description='Продолжительность экскурсии (в минутах)'),
    'category_id': fields.Integer(required=True, description='ID категории экскурсии'),
    'event_type_id': fields.Integer(required=True, description='ID типа мероприятия'),
    'is_active': fields.Boolean(required=True, description='Активна ли экскурсия'),
})

data_param = {
    'in': 'formData',
    'type': 'string',
    'required': True,
    'description': 'JSON-строка с данными экскурсии (см. модель ExcursionData)'
}

photos_param = {
    'in': 'formData',
    'type': 'file',
    'required': False,
    'description': 'Файлы изображений экскурсии (можно несколько)',
    'multiple': True
}

reservation_model = api.model('ReservationRequest', {
    'session_id': fields.Integer(required=True, description='ID сеанса')
})

cancel_model = api.model('CancelReservationRequest', {
    'reservation_id': fields.Integer(required=True, description='ID бронирования')
})
