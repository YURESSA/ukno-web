from flask_jwt_extended import create_access_token

from .models import User
from ..core import db


def create_user(username, email, password):
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return None

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return access_token
    return None
