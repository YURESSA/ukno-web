import os
import uuid

from werkzeug.utils import secure_filename

from backend.core.config import Config

UPLOAD_FOLDER = Config.UPLOAD_FOLDER


def save_image(file):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)

    unique_suffix = uuid.uuid4().hex
    filename = f"{name}_{unique_suffix}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)
    return filepath.replace("\\", "/")
