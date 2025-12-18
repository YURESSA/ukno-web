from backend.core import db
from backend.core.models.event_models import AgeCategory
from typing import Optional

def get_all_age_categories() -> list[AgeCategory]:
    """Получение всех возрастных категорий."""
    return AgeCategory.query.all()


def get_age_category_by_name(name: str) -> Optional[AgeCategory]:
    """Поиск возрастной категории по имени."""
    return AgeCategory.query.filter_by(age_category_name=name).first()


def get_age_category_by_id(category_id: int) -> Optional[AgeCategory]:
    """Поиск возрастной категории по ID."""
    return AgeCategory.query.get(category_id)


def create_age_category(name: str) -> AgeCategory:
    """Создание новой возрастной категории."""
    age_category = AgeCategory(age_category_name=name)
    db.session.add(age_category)
    db.session.commit()
    return age_category


def delete_age_category(category: AgeCategory) -> None:
    """Удаление возрастной категории."""
    db.session.delete(category)
    db.session.commit()
