from typing import Optional

from backend.core import db
from backend.core.models.event_models import Category


def get_all_categories() -> list[Category]:
    """Получение всех категорий экскурсий."""
    return Category.query.all()


def get_category_by_name(name: str) -> Optional[Category]:
    """Поиск категории по имени."""
    return Category.query.filter_by(category_name=name).first()


def get_category_by_id(category_id: int) -> Optional[Category]:
    """Поиск категории по ID."""
    return Category.query.get(category_id)


def create_category(name: str) -> Category:
    """Создание новой категории."""
    category = Category(category_name=name)
    db.session.add(category)
    db.session.commit()
    return category


def delete_category(category: Category) -> None:
    """Удаление категории."""
    db.session.delete(category)
    db.session.commit()
