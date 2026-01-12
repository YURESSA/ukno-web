from datetime import datetime
from typing import Optional

from backend.core import db
from backend.core.models.ref_models import CompanyHistory


def get_all_history() -> list[CompanyHistory]:
    """Получение всех событий истории компании."""
    return CompanyHistory.query.order_by(CompanyHistory.date).all()


def get_history_by_id(history_id: int) -> Optional[CompanyHistory]:
    """Получение события по ID."""
    return db.session.get(CompanyHistory, history_id)


def create_history(title: str, link: str, date_str: str, description: str) -> CompanyHistory:
    """Создание нового события истории компании."""
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD")

    item = CompanyHistory(
        title=title,
        link=link,
        date=event_date,
        description=description
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_history(item: CompanyHistory, title: str, link: str, date_str: str, description: str) -> CompanyHistory:
    """Обновление существующего события."""
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD")

    item.title = title
    item.link = link
    item.date = event_date
    item.description = description
    db.session.commit()
    return item


def delete_history(item: CompanyHistory) -> None:
    """Удаление события."""
    db.session.delete(item)
    db.session.commit()


def validate_history_data(data: dict) -> tuple[str, str, str, str] | None:
    """
    Проверка и извлечение обязательных полей для CompanyHistory.
    Возвращает кортеж (title, link, date_str, description) или None при ошибке.
    """
    title = data.get('title')
    if not title:
        raise ValueError('Поле title обязательно')

    link = data.get('link')

    date_str = data.get('date')
    if not date_str:
        raise ValueError('Поле date обязательно')

    description = data.get('description')
    if not description:
        raise ValueError('Поле description обязательно')

    return title, link, date_str, description
