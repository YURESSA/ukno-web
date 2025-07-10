import re

from backend.core.config import Config
from backend.core.services.calendar_utilits import create_ical_from_reservation
from backend.core.services.utilits import send_email, generate_reset_token


def send_reservation_confirmation_email(reservation, user):
    session = reservation.session
    excursion = session.excursion if session else None
    session_time = session.start_datetime.strftime(
        '%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'

    subject = "Подтверждение бронирования экскурсии"
    recipient = reservation.email or user.email
    display_name = reservation.full_name or recipient

    body_text = (
        f"Здравствуйте, {display_name}!\n\n"
        f"Вы успешно записались на экскурсию:\n"
        f"Название: {excursion.title if excursion else 'Экскурсия'}\n"
        f"Дата и время: {session_time}\n"
        f"Количество участников: {reservation.participants_count}\n\n"
        f"Место проведения: {excursion.place if excursion and excursion.place else 'уточняется'}\n"
        f"Контактный email: {excursion.contact_email if excursion and excursion.contact_email else 'не указан'}\n\n"
        "Во вложении вы найдете файл с приглашением в календарь (.ics), "
        "который можно добавить в ваш календарь.\n\n"
        "Спасибо за бронирование!"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте, <strong>{display_name}</strong>!</p>
        <p>Вы успешно записались на экскурсию:</p>
        <ul>
          <li><strong>Название:</strong> {excursion.title if excursion else 'Экскурсия'}</li>
          <li><strong>Дата и время:</strong> {session_time}</li>
          <li><strong>Количество участников:</strong> {reservation.participants_count}</li>
          <li><strong>Место проведения:</strong> {excursion.place if excursion and excursion.place else 'уточняется'}</li>
          <li><strong>Контактный email:</strong> {excursion.contact_email if excursion and excursion.contact_email else 'не указан'}</li>
        </ul>
        <p>Во вложении вы найдете файл с приглашением в календарь (<code>.ics</code>), который можно добавить в ваш календарь.</p>
        <p>Спасибо за бронирование!</p>
      </body>
    </html>
    """

    ics_bytes = create_ical_from_reservation(reservation)

    try:
        send_email(
            subject=subject,
            recipient=recipient,
            body=body_text,
            body_html=body_html,
            attachments=[("reservation.ics", ics_bytes, "text/calendar")]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_reservation_cancellation_email(user, reservation):
    excursion = reservation.session.excursion if reservation.session else None
    session = reservation.session

    subject = "Бронирование аннулировано"

    date_str = session.start_datetime.strftime('%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'
    session_id_str = session.session_id if session else 'неизвестен'
    excursion_title = excursion.title if excursion else 'Экскурсия'

    body_text = (
            f"Здравствуйте, {user.full_name}!\n\n"
            f"Ваше бронирование на экскурсию «{excursion_title}» "
            f"(ID сессии: {session_id_str}), запланированную на {date_str}, было аннулировано администратором."
            + (
                "\nСредства за бронирование будут возвращены в ближайшее время."
                if reservation.payment and getattr(reservation.payment, 'status', '') == "succeeded"
                else ""
            )
            + "\n\nПриносим извинения за возможные неудобства.\n"
              "Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам."
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте, <strong>{user.full_name}</strong>!</p>
        <p>Ваше бронирование на экскурсию <strong>«{excursion_title}»</strong> (ID сессии: <strong>{session_id_str}</strong>), запланированную на <strong>{date_str}</strong>, было аннулировано администратором.</p>
        {'<p><strong>Средства за бронирование будут возвращены в ближайшее время.</strong></p>' if reservation.payment and getattr(reservation.payment, 'status', '') == "succeeded" else ''}
        <p>Приносим извинения за возможные неудобства.</p>
        <p>Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам.</p>
      </body>
    </html>
    """

    try:
        send_email(subject=subject, recipient=user.email, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_excursion_deletion_email(resident, excursion, csv_data):
    subject = "Удалена экскурсия и отменены сессии"
    recipient = resident.email

    body_text = (
        "Здравствуйте!\n\n"
        f"Экскурсия «{excursion.title}» и все её сессии были удалены.\n"
        "В приложении — список всех отменённых бронирований.\n"
        "Спасибо за использование платформы!"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте!</p>
        <p>Экскурсия <strong>«{excursion.title}»</strong> и все её сессии были удалены.</p>
        <p>В приложении — список всех отменённых бронирований.</p>
        <p>Спасибо за использование платформы!</p>
      </body>
    </html>
    """

    title_slug = re.sub(r'\W+', '_', excursion.title.lower())
    filename = f"отменённые_бронирования_{title_slug}.csv"

    try:
        send_email(
            subject=subject,
            recipient=recipient,
            body=body_text,
            body_html=body_html,
            attachments=[(filename, csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении экскурсии: {e}")


def send_session_cancellation_email(reservation, excursion_name, session):
    subject = "Отмена экскурсионной сессии"
    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body_text = (
            f"Здравствуйте, {reservation.full_name}!\n\n"
            f"Сессия экскурсии «{excursion_name}» (ID {session.session_id}) на "
            f"{session.start_datetime.strftime('%d.%m.%Y %H:%M')} отменена.\n"
            "Ваше бронирование автоматически аннулировано."
            + (
                "\nСредства будут возвращены в ближайшее время."
                if reservation.payment and reservation.payment.status == "succeeded" else ""
            )
            + "\n\nПриносим извинения за возможные неудобства."
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте, <strong>{reservation.full_name}</strong>!</p>
        <p>Сессия экскурсии <strong>«{excursion_name}»</strong> (ID <strong>{session.session_id}</strong>) 
           на <strong>{session.start_datetime.strftime('%d.%m.%Y %H:%M')}</strong> отменена.</p>
        <p>Ваше бронирование автоматически аннулировано.</p>
        {"<p><strong>Средства будут возвращены в ближайшее время.</strong></p>" if reservation.payment and reservation.payment.status == "succeeded" else ""}
        <p>Приносим извинения за возможные неудобства.</p>
      </body>
    </html>
    """

    try:
        send_email(subject=subject, recipient=recipient, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма об отмене сессии: {e}")


def send_session_deletion_email(deleter_email, excursion_name, session_id, csv_data):
    subject = "Список отменённых бронирований по удалённой сессии"

    body_text = (
        f"Сессия экскурсии «{excursion_name}» (ID {session_id}) была удалена.\n\n"
        f"Во вложении — список всех отменённых по этой сессии бронирований.\n"
        f"Если возвраты были оформлены автоматически — дополнительных действий не требуется."
    )

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Здравствуйте!</p>
            <p>Сессия экскурсии <strong>«{excursion_name}»</strong> (ID <strong>{session_id}</strong>) была <strong>удалена</strong>.</p>
            <p>Во вложении вы найдёте CSV-файл со списком всех отменённых по этой сессии бронирований.</p>
            <p>Если возвраты были оформлены автоматически, дополнительных действий не требуется.</p>
            <br>
            <p>С уважением,<br>Система управления экскурсиями</p>
        </body>
    </html>
    """

    excursion_slug = re.sub(r'\W+', '_', excursion_name.lower())
    filename = f"отменённые_бронирования_{excursion_slug}_сессия_{session_id}.csv"

    try:
        send_email(
            subject=subject,
            recipient=deleter_email,
            body=body_text,
            body_html=body_html,
            attachments=[(filename, csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении сессии: {e}")


def send_reservation_refund_email(reservation):
    subject = "Ваше бронирование отменено — возврат средств"

    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body_text = (
        f"Здравствуйте, {reservation.full_name}!\n\n"
        f"Ваше бронирование на экскурсию "
        f"«{reservation.session.excursion.title}» "
        f"на {reservation.session.start_datetime.strftime('%d.%m.%Y в %H:%M')} было успешно отменено.\n\n"
        f"Мы оформили возврат средств на тот же способ оплаты, который использовался при покупке.\n"
        f"Сумма возврата: {reservation.payment.amount if reservation.payment else 'не указана'} "
        f"{reservation.payment.currency if reservation.payment else 'RUB'}\n\n"
        f"Если у вас возникли вопросы, пожалуйста, свяжитесь с нашей службой поддержки.\n\n"
        f"С уважением,\nКоманда поддержки"
    )

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; font-size: 15px; color: #333;">
            <p>Здравствуйте, <strong>{reservation.full_name}</strong>!</p>

            <p>Ваше бронирование на экскурсию<br>
            <strong>«{reservation.session.excursion.title}»</strong><br>
            на <strong>{reservation.session.start_datetime.strftime('%d.%m.%Y в %H:%M')}</strong> было успешно отменено.</p>

            <p>Мы оформили возврат средств на тот же способ оплаты, который использовался при покупке.</p>

            <p><strong>Сумма возврата:</strong><br>
            {reservation.payment.amount if reservation.payment else 'не указана'} 
            {reservation.payment.currency if reservation.payment else 'RUB'}</p>

            <p>Если у вас возникли вопросы или вы считаете, что отмена произошла по ошибке, пожалуйста, свяжитесь с нашей службой поддержки.</p>

            <p>Спасибо, что выбираете нас!<br>
            <em>С уважением,<br>Команда поддержки</em></p>
        </body>
    </html>
    """

    try:
        send_email(subject=subject, recipient=recipient, body=body_text, attachments=None, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма о возврате: {e}")


def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = f"{Config.FRONTEND_URL}reset-password?token={token}"

    subject = "Сброс пароля"

    body_text = f"""Здравствуйте, {user.full_name}!

Для сброса пароля перейдите по ссылке ниже:
{reset_url}

Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо."""

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
            <p>Здравствуйте, <strong>{user.full_name}</strong>!</p>
            <p>Для сброса пароля перейдите по ссылке ниже:</p>
            <p><a href="{reset_url}">Сбросить пароль</a></p>
            <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
        </body>
    </html>
    """

    send_email(subject=subject, recipient=user.email, body=body_text, body_html=body_html)
