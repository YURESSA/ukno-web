from http import HTTPStatus

from backend.core import db


def reorder_photos(event, photo_ids):
    """Reorder the complete current photo set; the caller must verify ownership."""
    if not isinstance(photo_ids, list) or any(type(photo_id) is not int for photo_id in photo_ids):
        return {"message": "Передайте список идентификаторов фотографий"}, HTTPStatus.BAD_REQUEST
    current = {photo.photo_id: photo for photo in event.photos}
    if len(photo_ids) != len(current) or set(photo_ids) != set(current):
        return {"message": "Список фотографий изменился. Обновите событие и повторите попытку"}, HTTPStatus.CONFLICT

    if all(current[photo_id].order_index == index for index, photo_id in enumerate(photo_ids)):
        return {"photos": [current[photo_id].to_dict() for photo_id in photo_ids]}, HTTPStatus.OK
    for index, photo_id in enumerate(photo_ids):
        current[photo_id].order_index = index
    if getattr(event, 'moderation_status', None) == 'approved':
        event.moderation_status = 'pending'
        event.moderation_comment = None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {"message": "Не удалось сохранить порядок фотографий"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return {"photos": [current[photo_id].to_dict() for photo_id in photo_ids]}, HTTPStatus.OK
