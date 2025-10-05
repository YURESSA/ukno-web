from datetime import timedelta

from ics import Calendar, Event


def create_ical_from_reservation(reservation):
    c = Calendar()
    e = Event()

    e.name = f"Событие: {reservation.session.event.title}"
    e.begin = reservation.session.start_datetime
    duration_minutes = getattr(reservation.session.event, 'duration', 60)
    e.duration = timedelta(minutes=duration_minutes)

    e.location = reservation.session.event.place or ""
    e.description = f"Бронирование экскурсии. Участников: {reservation.participants_count}"

    c.events.add(e)
    return c.serialize().encode('utf-8')
