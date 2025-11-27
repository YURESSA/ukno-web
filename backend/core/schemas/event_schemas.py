from flask_restx import fields

from backend.core import api

data_param = {
    'in': 'formData',
    'type': 'string',
    'required': True,
    'description': 'JSON-строка с данными экскурсии (см. модель EventData)'
}

photos_param = {
    'in': 'formData',
    'type': 'file',
    'required': False,
    'description': 'Файлы изображений экскурсии (можно несколько)',
    'multiple': True
}

reservation_model = api.model("Reservation", {
    "session_id": fields.Integer(required=True),
    "full_name": fields.String(required=True),
    "phone_number": fields.String(required=True),
    "email": fields.String(required=True),
    "participants_count": fields.Integer(required=True, min=1)
})

cancel_model = api.model('CancelReservationRequest', {
    'reservation_id': fields.Integer(required=True, description='ID бронирования')
})

event_model = api.model('Event', {
    'excursion_id': fields.Integer(readonly=True, description='ID экскурсии'),
    'title': fields.String(required=True, description='Название экскурсии'),
    'description': fields.String(description='Описание'),
    'duration': fields.Integer(description='Продолжительность (мин)'),
    'place': fields.String(description='Место проведения'),
    'conducted_by': fields.String(description='Экскурсовод'),
    'is_active': fields.Boolean(description='Активна ли экскурсия'),
    'working_hours': fields.String(description='Часы работы'),
    'contact_email': fields.String(description='Контактный email'),
    'iframe_url': fields.String(description='URL iframe карты'),
    'telegram': fields.String(description='Telegram'),
    'vk': fields.String(description='VK'),
    'distance_to_center': fields.Float(description='Расстояние до центра (метры)'),
    'time_to_nearest_stop': fields.Float(description='Время до ближайшей остановки (мин)'),
})

event_create_model = api.model('EventCreate', {
    'title': fields.String(required=True, description='Название экскурсии'),
    'description': fields.String(description='Описание'),
    'duration': fields.Integer(description='Продолжительность (мин)'),
    'category': fields.String(required=True, description='Категория'),
    'format_type': fields.String(required=True, description='Формат мероприятия'),
    'age_category': fields.String(required=True, description='Возрастная категория'),
    'place': fields.String(required=True, description='Место проведения'),
    'conducted_by': fields.String(description='Экскурсовод'),
    'is_active': fields.Boolean(description='Активна ли экскурсия'),
    'working_hours': fields.String(description='Часы работы'),
    'contact_email': fields.String(description='Контактный email'),
    'iframe_url': fields.String(description='URL iframe карты'),
    'telegram': fields.String(description='Telegram'),
    'vk': fields.String(description='VK'),
    'sessions': fields.List(fields.Nested(api.model('SessionInput', {
        'start_datetime': fields.String(required=True, description='Дата и время начала в ISO формате'),
        'max_participants': fields.Integer(description='Макс. участников'),
        'cost': fields.Float(description='Стоимость'),
    }))),
    'tags': fields.List(fields.String(description='Теги')),
})

session_model = api.model('Session', {
    'session_id': fields.Integer(readonly=True, description='ID сессии'),
    'start_datetime': fields.String(description='Дата и время начала'),
    'max_participants': fields.Integer(description='Максимум участников'),
    'cost': fields.Float(description='Стоимость'),
})

session_patch_model = api.model('EventSessionPatch', {
    'start_datetime': fields.String(description='Дата и время начала в формате ISO 8601',
                                    example='2025-06-10T11:00:00'),
    'max_participants': fields.Integer(description='Максимальное количество участников', example=20),
    'cost': fields.Float(description='Стоимость участия в рублях', example=500)
})
photo_model = api.model('Photo', {
    'photo_id': fields.Integer(readonly=True, description='ID фото'),
    'filename': fields.String(description='Имя файла'),
    'photo_url': fields.String(description='URL фото'),
})

role_model = api.model('Role', {
    'name': fields.String(required=True, description='Название роли')
})
