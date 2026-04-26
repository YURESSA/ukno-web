from typing import Type, Any


def get_model_by_name(model: Type[Any], field_name: str, value: Any, error_message: str) -> Any:
    """
    Получает объект модели по значению указанного поля.

    :param model: SQLAlchemy модель
    :param field_name: имя поля модели для фильтра
    :param value: значение для поиска
    :param error_message: сообщение ошибки, если объект не найден
    :return: объект модели
    :raises ValueError: если объект не найден
    """
    instance = model.query.filter(getattr(model, field_name) == value).first()
    if not instance:
        raise ValueError(error_message)
    return instance
