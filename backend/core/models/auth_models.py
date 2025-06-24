from werkzeug.security import generate_password_hash, check_password_hash

from backend.core import db


class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.role_name}>"

    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name
        }


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)

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
