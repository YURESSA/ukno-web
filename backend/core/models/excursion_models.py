from datetime import datetime

from sqlalchemy import func

from backend.core import db

excursion_tags = db.Table(
    'excursion_tags',
    db.Column('excursion_id', db.Integer, db.ForeignKey('excursions.excursion_id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.tag_id'), primary_key=True)
)


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)

    excursions = db.relationship("Excursion", back_populates="category", lazy=True)

    def __str__(self):
        return f"Category(id={self.category_id}, name={self.category_name})"

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name
        }


class FormatType(db.Model):
    __tablename__ = 'format_types'

    format_type_id = db.Column(db.Integer, primary_key=True)
    format_type_name = db.Column(db.String(255), nullable=False)

    excursions = db.relationship("Excursion", back_populates="format_type", lazy=True)

    def __str__(self):
        return f"FormatType(id={self.format_type_id}, name={self.format_type_name})"

    def to_dict(self):
        return {
            'format_type_id': self.format_type_id,
            'format_type_name': self.format_type_name
        }


class AgeCategory(db.Model):
    __tablename__ = 'age_categories'

    age_category_id = db.Column(db.Integer, primary_key=True)
    age_category_name = db.Column(db.String(255), nullable=False)

    excursions = db.relationship("Excursion", back_populates="age_category", lazy=True)

    def __str__(self):
        return f"AgeCategory(id={self.age_category_id}, name={self.age_category_name})"

    def to_dict(self):
        return {
            'age_category_id': self.age_category_id,
            'age_category_name': self.age_category_name
        }


class Excursion(db.Model):
    __tablename__ = 'excursions'

    excursion_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    format_type_id = db.Column(db.Integer, db.ForeignKey('format_types.format_type_id'), nullable=False)
    age_category_id = db.Column(db.Integer, db.ForeignKey('age_categories.age_category_id'), nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    place = db.Column(db.String(255), nullable=False)
    conducted_by = db.Column(db.String(255), nullable=True)

    working_hours = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    iframe_url = db.Column(db.Text, nullable=True)
    telegram = db.Column(db.String(100), nullable=True)
    vk = db.Column(db.String(100), nullable=True)

    category = db.relationship("Category", back_populates="excursions")
    format_type = db.relationship("FormatType", back_populates="excursions")
    age_category = db.relationship("AgeCategory", back_populates="excursions")

    distance_to_center = db.Column(db.Float, nullable=True)
    distance_to_stop = db.Column(db.Float, nullable=True)

    photos = db.relationship("ExcursionPhoto", back_populates="excursion", cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship("ExcursionSession", back_populates="excursion", cascade="all, delete-orphan", lazy=True)
    tags = db.relationship("Tag", secondary=excursion_tags, back_populates="excursions", lazy='subquery')

    def __str__(self):
        return f"Excursion(id={self.excursion_id}, title={self.title})"

    def to_dict(self, include_related=False):
        data = {
            'excursion_id': self.excursion_id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'category': self.category.to_dict() if self.category else None,
            'format_type': self.format_type.to_dict() if self.format_type else None,
            'age_category': self.age_category.to_dict() if self.age_category else None,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'place': self.place,
            'conducted_by': self.conducted_by,
            'working_hours': self.working_hours,
            'contact_email': self.contact_email,
            'iframe_url': self.iframe_url,
            'telegram': self.telegram,
            'vk': self.vk,
            "distance_to_center": self.distance_to_center,
            "time_to_nearest_stop": self.distance_to_stop,
            'photos': [photo.to_dict() for photo in self.photos],
            'sessions': [session.to_dict() for session in self.sessions],
            'tags': [tag.to_dict() for tag in self.tags]
        }
        if include_related:
            data['reservations'] = [
                reservation.to_dict()
                for session in self.sessions
                for reservation in session.reservations
            ]

        return data


class ExcursionPhoto(db.Model):
    __tablename__ = 'excursion_photos'

    photo_id = db.Column(db.Integer, primary_key=True)
    excursion_id = db.Column(db.Integer, db.ForeignKey('excursions.excursion_id'), nullable=False)
    photo_url = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    excursion = db.relationship("Excursion", back_populates="photos")

    def __str__(self):
        return f"ExcursionPhoto(id={self.photo_id}, excursion_id={self.excursion_id}, " \
               f"photo_url={self.photo_url}, order_index={self.order_index})"

    def to_dict(self):
        return {
            'photo_id': self.photo_id,
            'excursion_id': self.excursion_id,
            'photo_url': self.photo_url,
            'order_index': self.order_index
        }


class ExcursionSession(db.Model):
    __tablename__ = 'excursion_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    excursion_id = db.Column(db.Integer, db.ForeignKey('excursions.excursion_id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    max_participants = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    excursion = db.relationship("Excursion", back_populates="sessions")
    reservations = db.relationship(
        "Reservation",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __str__(self):
        return f"ExcursionSession(id={self.session_id}, excursion_id={self.excursion_id}, " \
               f"start_datetime={self.start_datetime}, max_participants={self.max_participants}, " \
               f"cost={self.cost})"

    def booked_count(self):
        return db.session.query(
            func.coalesce(func.sum(Reservation.participants_count), 0)
        ).filter_by(
            session_id=self.session_id,
            is_cancelled=False
        ).scalar()

    def to_dict(self):
        booked = self.booked_count()
        return {
            'session_id': self.session_id,
            'start_datetime': self.start_datetime.isoformat(),
            'max_participants': self.max_participants,
            'cost': str(self.cost),
            'booked': booked,
            'available': self.max_participants - booked
        }


class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('excursion_sessions.session_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Новые поля
    full_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    participants_count = db.Column(db.Integer, nullable=False, default=1)
    is_cancelled = db.Column(db.Boolean, default=False)

    session = db.relationship("ExcursionSession", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")

    def __str__(self):
        return (f"Reservation(id={self.reservation_id}, session_id={self.session_id}, "
                f"user_id={self.user_id}, full_name={self.full_name}, phone={self.phone_number}, "
                f"email={self.email}, participants={self.participants_count}, cancelled={self.is_cancelled}, "
                f"booked_at={self.booked_at})")

    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'booked_at': self.booked_at.isoformat(),
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'participants_count': self.participants_count,
            'is_cancelled': self.is_cancelled
        }


class Tag(db.Model):
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    excursions = db.relationship("Excursion", secondary=excursion_tags, back_populates="tags", lazy='subquery')

    def __str__(self):
        return f"Tag(id={self.tag_id}, name={self.name})"

    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'name': self.name,
        }
