from http import HTTPStatus

from backend.core import db
from backend.core.services.event_services.event_crud import get_event


def prepare_resident_event_edit(event):
    """Persist with the content mutation in the caller's transaction."""
    if event.moderation_status == 'approved':
        event.moderation_status = 'pending'
        event.moderation_comment = None


def change_moderation_status(event_id, target, comment=None):
    event = get_event(event_id)
    if event is None:
        return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
    if target == 'returned':
        if not isinstance(comment, str) or not comment.strip():
            return {"message": "Укажите комментарий для возврата"}, HTTPStatus.BAD_REQUEST
        if event.moderation_status not in ('pending', 'approved'):
            return {"message": "Событие уже возвращено на доработку"}, HTTPStatus.CONFLICT
        event.moderation_comment = comment.strip()
    elif target == 'pending':
        if event.moderation_status != 'returned':
            return {"message": "Повторно отправить можно только возвращённое событие"}, HTTPStatus.CONFLICT
        event.moderation_comment = None
    else:
        raise ValueError("Unsupported moderation status")
    event.moderation_status = target
    db.session.commit()
    return {"excursion": event.to_dict()}, HTTPStatus.OK
