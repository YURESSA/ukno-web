# backend/cleanup_reservations.py
from datetime import datetime, timedelta

from backend.core import db, create_app
from backend.core.models.excursion_models import Reservation


def cleanup_unpaid_reservations():
    threshold = datetime.utcnow() - timedelta(minutes=15)
    unpaid_old = Reservation.query.filter(
        Reservation.is_paid == False,
        Reservation.booked_at < threshold,
        Reservation.is_cancelled == False
    ).all()
    for reservation in unpaid_old:
        db.session.delete(reservation)
    db.session.commit()
    print(f"Удалено {len(unpaid_old)} неоплаченных броней старше 15 минут.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        cleanup_unpaid_reservations()
