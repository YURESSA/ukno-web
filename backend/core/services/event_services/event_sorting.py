from typing import Optional

from sqlalchemy import Subquery, desc, asc
from sqlalchemy.orm import Query

from backend.core.models.event_models import Event


def apply_sorting(query: Query, sort_key: Optional[str], subquery: Subquery) -> Query:
    """
    Применяет сортировку к SQLAlchemy Query по указанным полям.

    :param query: SQLAlchemy Query объект для модели Event
    :param sort_key: Строка с полями для сортировки, разделёнными запятыми.
                     Можно использовать '-' для сортировки по убыванию (например, "-price").
                     Поддерживаются поля Event и агрегированные значения из subquery: 'price', 'time'.
    :param subquery: Подзапрос с агрегированными значениями (например, min_cost, min_date)
    :return: Обновленный Query с примененной сортировкой
    """
    if not sort_key:
        return query

    sort_fields = [s.strip() for s in sort_key.split(",") if s.strip()]
    order_criteria = []

    for field in sort_fields:
        is_desc = field.startswith("-")
        field_name = field.lstrip("-")

        if field_name == "price":
            order = desc(subquery.c.min_cost) if is_desc else asc(subquery.c.min_cost)
        elif field_name == "time":
            order = desc(subquery.c.min_date) if is_desc else asc(subquery.c.min_date)
        elif hasattr(Event, field_name):
            column = getattr(Event, field_name)
            order = desc(column) if is_desc else asc(column)
        else:
            continue

        order_criteria.append(order)

    if order_criteria:
        query = query.order_by(*order_criteria)

    return query
