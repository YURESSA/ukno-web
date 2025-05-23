import os
import uuid

from werkzeug.utils import secure_filename

from backend.core import mail
from backend.core.config import Config

UPLOAD_FOLDER = Config.UPLOAD_FOLDER


def save_image(file, subfolder=""):
    folder_path = os.path.join(UPLOAD_FOLDER, subfolder)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    unique_suffix = uuid.uuid4().hex
    filename = f"{name}_{unique_suffix}{ext}"

    filepath = os.path.join(folder_path, filename)
    file.save(filepath)

    return filepath.replace("\\", "/")


def get_model_by_name(model, field_name, value, error_message):
    instance = model.query.filter(getattr(model, field_name) == value).first()
    if not instance:
        raise ValueError(error_message)
    return instance


def remove_file_if_exists(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")


from flask_mail import Message

from io import BytesIO


def send_email(subject, recipient, body, attachments=None):
    """
    attachments: list of tuples (filename, content_str)
    """
    msg = Message(subject=subject, recipients=[recipient], body=body)

    if attachments:
        for filename, content in attachments:
            # content — строка, конвертируем в байты
            data = BytesIO(content.encode('utf-8'))
            msg.attach(filename, "text/csv", data.read())

    mail.send(msg)
