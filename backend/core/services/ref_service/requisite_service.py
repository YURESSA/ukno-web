from backend.core import db
from backend.core.models.ref_models import Requisite
from backend.core.utilits.file_utils import save_file, remove_file_if_exists


def get_all_requisites():
    return Requisite.query.order_by(Requisite.id.desc()).all()

def get_requisite_by_id(requisite_id: int):
    return db.session.get(Requisite, requisite_id)

def create_requisite(title: str, file):
    if not title:
        raise ValueError('Название обязательно')
    if not file:
        raise ValueError('Файл обязателен')

    file_path = save_file(file, 'requisites')

    item = Requisite(title=title, file=file_path)
    db.session.add(item)
    db.session.commit()
    return item


def update_requisite(item: Requisite, title: str):
    if not title:
        raise ValueError('Название обязательно')
    item.title = title
    db.session.commit()
    return item


def replace_requisite_file(item: Requisite, file):
    if not file:
        raise ValueError('Файл не выбран')

    # Удаляем старый файл
    if item.file:
        remove_file_if_exists(item.file)

    # Сохраняем новый
    item.file = save_file(file, 'requisites')
    db.session.commit()
    return item.file


def delete_requisite(item: Requisite):
    if item.file:
        remove_file_if_exists(item.file)
    db.session.delete(item)
    db.session.commit()


def delete_requisite_file(item):
    """
    Удаляет файл реквизита с диска и очищает поле item.file
    """
    if item.file:
        remove_file_if_exists(item.file)
        item.file = None
        from backend.core import db
        db.session.commit()
