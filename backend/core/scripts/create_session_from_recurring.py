from datetime import datetime, timedelta

from backend.core.models.excursion_models import ExcursionSession
from backend.core.models.excursion_models import RecurringSchedule

from backend.core import db


def create_sessions_from_recurring():
    today = datetime.utcnow().date()
    future_date = today + timedelta(days=28)  # создаём сессии на 4 недели вперёд

    schedules = RecurringSchedule.query.all()

    for schedule in schedules:
        # Текущий счетчик повторов для расписания
        current_repeats = schedule.count_of_repeats or 0

        # Максимальное количество повторов
        max_repeats = schedule.repeats

        # Создаем сессии по дням в интервале
        for day_offset in range((future_date - today).days + 1):
            day = today + timedelta(days=day_offset)

            # Приведение weekday к python.weekday() (Monday=0 ... Sunday=6)
            # В модели: 0=воскресенье, ..., 6=суббота
            python_weekday = (schedule.weekday + 6) % 7

            if day.weekday() == python_weekday:
                # Проверяем, не превысили ли количество повторов
                if max_repeats != 0 and current_repeats >= max_repeats:
                    break

                # Формируем дату и время начала сессии
                session_start_datetime = datetime.combine(day, schedule.start_time)

                # Проверяем, существует ли уже такая сессия (по дате, времени и экскурсии)
                exists = ExcursionSession.query.filter_by(
                    excursion_id=schedule.excursion_id,
                    start_datetime=session_start_datetime
                ).first()

                if exists:
                    continue  # сессия уже есть — пропускаем

                # Создаем новую сессию с учетом стоимости из расписания
                new_session = ExcursionSession(
                    excursion_id=schedule.excursion_id,
                    start_datetime=session_start_datetime,
                    max_participants=schedule.max_participants,
                    cost=schedule.cost  # теперь берём из RecurringSchedule
                )

                db.session.add(new_session)

                # Увеличиваем счетчик повторов для расписания
                current_repeats += 1

        # Обновляем count_of_repeats в расписании
        schedule.count_of_repeats = current_repeats

    db.session.commit()


if __name__ == '__main__':
    create_sessions_from_recurring()
