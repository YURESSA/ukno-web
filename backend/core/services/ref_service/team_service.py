import os

from backend.core import db
from backend.core.models.ref_models import TeamMember
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


MAX_IMAGE_SIZE = 5 * 1024 * 1024


def _validate_and_save_photo(photo, folder: str) -> str:
    if not photo or not photo.filename:
        raise ValueError('Файл не выбран')

    if not photo.content_type.startswith('image/'):
        raise ValueError('Файл должен быть изображением')

    photo.seek(0, os.SEEK_END)
    size = photo.tell()
    photo.seek(0)

    if size > MAX_IMAGE_SIZE:
        raise ValueError('Размер файла не должен превышать 5 MB')

    return save_image(photo, folder)


def get_team_members():
    return TeamMember.query.all()


def create_team_member(full_name: str, description: str = None, photo=None):
    if not full_name:
        raise ValueError('Поле full_name обязательно')

    photo_path = None
    if photo:
        photo_path = _validate_and_save_photo(photo, 'team_photos')

    member = TeamMember(
        full_name=full_name,
        description=description,
        photo=photo_path
    )

    db.session.add(member)
    db.session.commit()
    return member


def update_team_member(member: TeamMember, full_name: str, description: str = None):
    if not full_name:
        raise ValueError('Поле full_name обязательно')

    member.full_name = full_name
    member.description = description
    db.session.commit()
    return member


def delete_team_member(member: TeamMember):
    if member.photo:
        remove_file_if_exists(member.photo)

    db.session.delete(member)
    db.session.commit()


def upload_team_photo(member: TeamMember, photo):
    photo_path = _validate_and_save_photo(photo, 'team_photos')

    if member.photo:
        remove_file_if_exists(member.photo)

    member.photo = photo_path
    db.session.commit()
    return photo_path


def delete_team_photo(member: TeamMember):
    if not member.photo:
        raise ValueError('Фото отсутствует')

    remove_file_if_exists(member.photo)
    member.photo = None
    db.session.commit()

def get_team_member_by_id(member_id: int) -> TeamMember | None:
    return TeamMember.query.get(member_id)