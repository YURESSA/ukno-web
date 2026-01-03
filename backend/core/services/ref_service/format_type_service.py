from backend.core import db
from backend.core.models.event_models import FormatType


def get_all_format_types():
    return FormatType.query.all()


def get_format_type(id):
    return db.session.get(FormatType, id)


def create_format_type(name: str) -> FormatType:
    if not name:
        raise ValueError('Поле name обязательно')

    if FormatType.query.filter_by(format_type_name=name).first():
        raise ValueError('Тип формата с таким именем уже существует')

    format_type = FormatType(format_type_name=name)
    db.session.add(format_type)
    db.session.commit()
    return format_type


def delete_format_type(format_type: FormatType):
    db.session.delete(format_type)
    db.session.commit()
