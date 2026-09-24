import re
from html import escape

from backend.core.config import Config
from backend.core.utilits.token_utils import generate_reset_token
from backend.core.utilits.email_utils import send_email
from backend.core.utilits.file_utils import create_ical_from_reservation


def send_reservation_confirmation_email(reservation, user):
    session = reservation.session
    event = session.event if session else None
    session_time = session.start_datetime.strftime(
        '%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'
    session_date = session.start_datetime.strftime(
        '%d.%m.%Y') if session and session.start_datetime else 'уточняется'
    session_clock = session.start_datetime.strftime(
        '%H:%M') if session and session.start_datetime else 'уточняется'

    recipient = reservation.email or user.email
    display_name = reservation.full_name or recipient
    title = event.title if event else 'Событие'
    place = event.place if event and event.place else 'Место уточняется'
    contact = (event.contact_email if event and event.contact_email
               else 'Контакт будет указан организатором')
    booking_id = getattr(reservation, 'reservation_id', None)
    booking_label = f"№ {booking_id}" if booking_id is not None else 'подтверждено'
    participants = reservation.participants_count
    participant_word = (
        'участник' if participants % 10 == 1 and participants % 100 != 11
        else 'участника' if participants % 10 in (2, 3, 4) and participants % 100 not in (12, 13, 14)
        else 'участников'
    )
    subject = f"Вы записаны: {title} — {session_date}"

    body_text = (
        f"Здравствуйте, {display_name}!\n\n"
        "Готово — ваше бронирование подтверждено.\n\n"
        f"{title}\n"
        f"Дата и время: {session_time}\n"
        f"Место: {place}\n"
        f"Гостей: {participants}\n"
        f"Номер бронирования: {booking_label}\n\n"
        "Что дальше:\n"
        "1. Добавьте событие в календарь — файл reservation.ics приложен к письму.\n"
        "2. Перед поездкой ещё раз проверьте дату, время и адрес.\n"
        f"3. Если появятся вопросы, напишите организатору: {contact}\n\n"
        "До встречи в Молодёжном бюро «5 этаж»!"
    )

    safe_name = escape(str(display_name))
    safe_title = escape(str(title))
    safe_place = escape(str(place))
    safe_contact = escape(str(contact))
    safe_booking_label = escape(str(booking_label))
    contact_html = (
        f'<a href="mailto:{safe_contact}" style="color:#ff6c36;text-decoration:none;">{safe_contact}</a>'
        if '@' in str(contact) else safe_contact
    )

    body_html = f"""
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{escape(subject)}</title>
      </head>
      <body style="margin:0;padding:0;background:#f3f0eb;color:#201f1d;font-family:Arial,Helvetica,sans-serif;">
        <div style="display:none;max-height:0;overflow:hidden;opacity:0;">
          Бронирование подтверждено — {safe_title}, {session_date} в {session_clock}.
        </div>
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#f3f0eb;">
          <tr>
            <td align="center" style="padding:32px 12px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:640px;background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 12px 32px rgba(43,37,30,.08);">
                <tr>
                  <td style="padding:34px 40px;background:#ff6c36;color:#ffffff;">
                    <div style="font-size:13px;line-height:18px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;opacity:.9;">Молодёжное бюро · 5 этаж</div>
                    <div style="margin-top:14px;font-size:30px;line-height:36px;font-weight:800;">Вы записаны!</div>
                    <div style="margin-top:8px;font-size:16px;line-height:24px;">Бронирование {safe_booking_label} подтверждено</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:36px 40px 12px;">
                    <div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{safe_name}</strong>!</div>
                    <div style="margin-top:12px;color:#66615b;font-size:15px;line-height:24px;">Сохраняйте письмо — здесь собрана вся информация о вашем посещении.</div>
                    <div style="margin-top:28px;font-size:25px;line-height:32px;font-weight:800;color:#201f1d;">{safe_title}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 40px 6px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td width="48%" valign="top" style="padding:18px;background:#fff3ed;border-radius:16px;">
                          <div style="font-size:12px;line-height:18px;color:#8a5b48;font-weight:700;text-transform:uppercase;letter-spacing:.8px;">Дата</div>
                          <div style="margin-top:7px;font-size:21px;line-height:28px;font-weight:800;">{session_date}</div>
                        </td>
                        <td width="4%"></td>
                        <td width="48%" valign="top" style="padding:18px;background:#fff3ed;border-radius:16px;">
                          <div style="font-size:12px;line-height:18px;color:#8a5b48;font-weight:700;text-transform:uppercase;letter-spacing:.8px;">Начало</div>
                          <div style="margin-top:7px;font-size:21px;line-height:28px;font-weight:800;">{session_clock}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:12px 40px 6px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border:1px solid #ebe7e1;border-radius:16px;">
                      <tr>
                        <td style="padding:18px 20px;border-bottom:1px solid #ebe7e1;">
                          <div style="font-size:12px;line-height:18px;color:#817a72;font-weight:700;text-transform:uppercase;letter-spacing:.7px;">Место проведения</div>
                          <div style="margin-top:6px;font-size:16px;line-height:24px;font-weight:700;">{safe_place}</div>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:18px 20px;">
                          <div style="font-size:12px;line-height:18px;color:#817a72;font-weight:700;text-transform:uppercase;letter-spacing:.7px;">Гости</div>
                          <div style="margin-top:6px;font-size:16px;line-height:24px;font-weight:700;">{participants} {participant_word}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:24px 40px 8px;">
                    <div style="font-size:18px;line-height:26px;font-weight:800;">Что дальше</div>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top:14px;">
                      <tr><td valign="top" width="30" style="padding:5px 0;color:#ff6c36;font-weight:800;">1.</td><td style="padding:5px 0;font-size:15px;line-height:23px;">Добавьте событие в календарь — файл <strong>reservation.ics</strong> приложен к письму.</td></tr>
                      <tr><td valign="top" width="30" style="padding:5px 0;color:#ff6c36;font-weight:800;">2.</td><td style="padding:5px 0;font-size:15px;line-height:23px;">Перед поездкой ещё раз проверьте дату, время и адрес.</td></tr>
                      <tr><td valign="top" width="30" style="padding:5px 0;color:#ff6c36;font-weight:800;">3.</td><td style="padding:5px 0;font-size:15px;line-height:23px;">Если появятся вопросы, напишите организатору: {contact_html}</td></tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:26px 40px 36px;">
                    <div style="padding:20px 22px;background:#282622;color:#ffffff;border-radius:16px;font-size:16px;line-height:24px;">
                      До встречи в Молодёжном бюро «5 этаж»!
                    </div>
                  </td>
                </tr>
              </table>
              <div style="max-width:560px;padding:18px 20px 0;color:#8a847d;font-size:12px;line-height:18px;text-align:center;">
                Это автоматическое подтверждение бронирования. Контакт организатора: {contact_html}
              </div>
            </td>
          </tr>
        </table>
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
    event = reservation.session.event if reservation.session else None
    session = reservation.session

    subject = "Бронирование аннулировано"

    date_str = session.start_datetime.strftime('%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'
    session_id_str = session.session_id if session else 'неизвестен'
    event_title = event.title if event else 'Событие'

    body_text = (
            f"Здравствуйте, {user.full_name}!\n\n"
            f"Ваше бронирование на событие «{event_title}» "
            f"(ID сессии: {session_id_str}), запланированную на {date_str}, было аннулировано администратором."
            + (
                "\nСредства за бронирование будут возвращены в ближайшее время."
                if reservation.payment and getattr(reservation.payment, 'status', '') == "succeeded"
                else ""
            )
            + "\n\nПриносим извинения за возможные неудобства.\n"
              "Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам."
    )

    refund_notice = (
        '<p><strong>Средства за бронирование будут возвращены в ближайшее время.</strong></p>'
        if reservation.payment and getattr(reservation.payment, 'status', '') == "succeeded"
        else ''
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте, <strong>{user.full_name}</strong>!</p>
        <p>Ваше бронирование на событие <strong>«{event_title}»</strong>
        (ID сессии: <strong>{session_id_str}</strong>), запланированную на <strong>{date_str}</strong>,
        было аннулировано администратором.</p>
        {refund_notice}
        <p>Приносим извинения за возможные неудобства.</p>
        <p>Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам.</p>
      </body>
    </html>
    """

    try:
        send_email(subject=subject, recipient=user.email, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_event_deletion_email(resident, event, csv_data):
    subject = "Удалено событие и отменены сессии"
    recipient = resident.email

    body_text = (
        "Здравствуйте!\n\n"
        f"Событие «{event.title}» и все его сессии были удалены.\n"
        "В приложении — список всех отменённых бронирований.\n"
        "Спасибо за использование платформы!"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте!</p>
        <p>Событие <strong>«{event.title}»</strong> и все его сессии были удалены.</p>
        <p>В приложении — список всех отменённых бронирований.</p>
        <p>Спасибо за использование платформы!</p>
      </body>
    </html>
    """

    title_slug = re.sub(r'\W+', '_', event.title.lower())
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
        print(f"Ошибка при отправке письма об удалении события: {e}")


def send_session_cancellation_email(reservation, event_name, session):
    subject = "Отмена сессии события"
    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body_text = (
            f"Здравствуйте, {reservation.full_name}!\n\n"
            f"Сессия события «{event_name}» (ID {session.session_id}) на "
            f"{session.start_datetime.strftime('%d.%m.%Y %H:%M')} отменена.\n"
            "Ваше бронирование автоматически аннулировано."
            + (
                "\nСредства будут возвращены в ближайшее время."
                if reservation.payment and reservation.payment.status == "succeeded" else ""
            )
            + "\n\nПриносим извинения за возможные неудобства."
    )

    refund_notice = (
        '<p><strong>Средства будут возвращены в ближайшее время.</strong></p>'
        if reservation.payment and reservation.payment.status == "succeeded"
        else ''
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Здравствуйте, <strong>{reservation.full_name}</strong>!</p>
        <p>Сессия события <strong>«{event_name}»</strong> (ID <strong>{session.session_id}</strong>)<br>
            на <strong>{session.start_datetime.strftime('%d.%m.%Y %H:%M')}</strong> отменена.</p>
        <p>Ваше бронирование автоматически аннулировано.</p>
        {refund_notice}
        <p>Приносим извинения за возможные неудобства.</p>
      </body>
    </html>
    """

    try:
        send_email(subject=subject, recipient=recipient, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма об отмене сессии: {e}")


def send_session_deletion_email(deleter_email, event_name, session_id, csv_data):
    subject = "Список отменённых бронирований по удалённой сессии"

    body_text = (
        f"Сессия события «{event_name}» (ID {session_id}) была удалена.\n\n"
        f"Во вложении — список всех отменённых по этой сессии бронирований.\n"
        f"Если возвраты были оформлены автоматически — дополнительных действий не требуется."
    )

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Здравствуйте!</p>
            <p>Сессия события <strong>«{event_name}»</strong> (ID <strong>{session_id}</strong>)
            была <strong>удалена</strong>.</p>
            <p>Во вложении вы найдёте CSV-файл со списком всех отменённых по этой сессии бронирований.</p>
            <p>Если возвраты были оформлены автоматически, дополнительных действий не требуется.</p>
            <br>
            <p>С уважением,<br>Система управления событиями</p>
        </body>
    </html>
    """

    event_slug = re.sub(r'\W+', '_', event_name.lower())
    filename = f"отменённые_бронирования_{event_slug}_сессия_{session_id}.csv"

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
        f"Ваше бронирование на событие "
        f"«{reservation.session.event.title}» "
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

            <p>Ваше бронирование на сессию события <strong>«{reservation.session.event.title}»</strong>
            (на <strong>{reservation.session.start_datetime.strftime('%d.%m.%Y в %H:%M')}</strong>)
            было успешно отменено.</p>

            <p>Мы оформили возврат средств на тот же способ оплаты, который использовался при покупке.</p>

            <p><strong>Сумма возврата:</strong><br>
            {reservation.payment.amount if reservation.payment else 'не указана'}
            {reservation.payment.currency if reservation.payment else 'RUB'}</p>

            <p>Если у вас возникли вопросы, свяжитесь с нашей службой поддержки.</p>

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
