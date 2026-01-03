from backend.core import db
from backend.core.models.ref_models import TrustReason


def get_all_trust_reasons():
    """Возвращает все причины доверия."""
    return TrustReason.query.order_by(TrustReason.id).all()


def create_trust_reason(title: str, description: str | None = None) -> TrustReason:
    """Создает новую причину доверия."""
    if not title:
        raise ValueError("Поле title обязательно")

    reason = TrustReason(title=title, description=description)
    db.session.add(reason)
    db.session.commit()
    return reason


def delete_trust_reason(reason_id: int):
    """Удаляет причину доверия по ID."""
    reason = db.session.get(TrustReason, reason_id)
    if not reason:
        raise ValueError("Причина не найдена")

    db.session.delete(reason)
    db.session.commit()
