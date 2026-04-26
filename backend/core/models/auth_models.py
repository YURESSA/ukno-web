import enum

from werkzeug.security import generate_password_hash, check_password_hash

from backend.core import db


class RoleEnum(enum.Enum):
    ADMIN = "admin"
    RESIDENT = "resident"
    USER = "user"

    def to_dict(self):
        """
        Возвращает словарь с id и названием роли.
        role_id — порядковый номер Enum (начиная с 1)
        """
        role_id = list(RoleEnum).index(self) + 1
        return {
            "role_id": role_id,
            "role_name": self.value
        }


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(
        db.Enum(RoleEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RoleEnum.USER
    )

    reservations = db.relationship(
        "Reservation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
