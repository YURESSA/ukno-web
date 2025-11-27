from datetime import datetime

from sqlalchemy import func

from backend.core import db

event_tags = db.Table(
    'event_tags',
    db.Column('event_id', db.Integer, db.ForeignKey('events.event_id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.tag_id'), primary_key=True)
)


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)

    events = db.relationship("Event", back_populates="category", lazy=True)

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

    events = db.relationship("Event", back_populates="format_type", lazy=True)

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

    events = db.relationship("Event", back_populates="age_category", lazy=True)

    def __str__(self):
        return f"AgeCategory(id={self.age_category_id}, name={self.age_category_name})"

    def to_dict(self):
        return {
            'age_category_id': self.age_category_id,
            'age_category_name': self.age_category_name
        }


class Event(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
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

    category = db.relationship("Category", back_populates="events")
    format_type = db.relationship("FormatType", back_populates="events")
    age_category = db.relationship("AgeCategory", back_populates="events")

    distance_to_center = db.Column(db.Float, nullable=True)
    time_to_nearest_stop = db.Column(db.Float, nullable=True)

    photos = db.relationship("EventPhoto", back_populates="event", cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship("EventSession", back_populates="event", cascade="all, delete-orphan", lazy=True)
    tags = db.relationship("Tag", secondary='event_tags', back_populates="events", lazy='subquery')

    creator = db.relationship("User", backref="events_created", foreign_keys=[created_by])

    def __str__(self):
        return f"Event(id={self.event_id}, title={self.title})"

    def to_dict(self, include_related=False):
        data = {
            'excursion_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'category': self.category.to_dict() if self.category else None,
            'format_type': self.format_type.to_dict() if self.format_type else None,
            'age_category': self.age_category.to_dict() if self.age_category else None,
            'created_by': self.creator.email if self.creator else None,
            'is_active': self.is_active,
            'place': self.place,
            'conducted_by': self.conducted_by,
            'working_hours': self.working_hours,
            'contact_email': self.contact_email,
            'iframe_url': self.iframe_url,
            'telegram': self.telegram,
            'vk': self.vk,
            "distance_to_center": self.distance_to_center,
            "time_to_nearest_stop": self.time_to_nearest_stop,
            'photos': [photo.to_dict() for photo in self.photos],
            'sessions': [
                session.to_dict()
                for session in sorted(self.sessions, key=lambda s: s.start_datetime)
            ],
            'tags': [tag.to_dict() for tag in self.tags]
        }
        if include_related:
            data['reservations'] = [
                reservation.to_dict()
                for session in self.sessions
                for reservation in session.reservations
            ]

        return data


class EventPhoto(db.Model):
    __tablename__ = 'event_photos'

    photo_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    photo_url = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    event = db.relationship("Event", back_populates="photos")

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

    def __str__(self):
        return f"EventPhoto(id={self.photo_id}, event_id={self.event_id}, " \
               f"photo_url={self.photo_url}, order_index={self.order_index})"

    def to_dict(self):
        return {
            'photo_id': self.photo_id,
            'excursion_id': self.event_id,
            'photo_url': self.photo_url,
            'order_index': self.order_index
        }


class EventSession(db.Model):
    __tablename__ = 'event_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    max_participants = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    event = db.relationship("Event", back_populates="sessions")
    reservations = db.relationship(
        "Reservation",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy=True
    )
    payments = db.relationship("Payment", back_populates="session")

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

    def __str__(self):
        return f"EventSession(id={self.session_id}, event_id={self.event_id}, " \
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
    session_id = db.Column(db.Integer, db.ForeignKey('event_sessions.session_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Новые поля
    full_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    participants_count = db.Column(db.Integer, nullable=False, default=1)
    is_cancelled = db.Column(db.Boolean, default=False)
    is_paid = db.Column(db.Boolean, default=False)

    session = db.relationship("EventSession", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")
    payment = db.relationship("Payment", back_populates="reservation", uselist=False)

    def __str__(self):
        return (f"Reservation(id={self.reservation_id}, session_id={self.session_id}, "
                f"user_id={self.user_id}, full_name={self.full_name}, phone={self.phone_number}, "
                f"email={self.email}, participants={self.participants_count}, cancelled={self.is_cancelled}, "
                f"booked_at={self.booked_at})")

    def to_dict(self):
        cost = float(self.session.cost) if self.session and self.session.cost is not None else None
        total = float(cost * self.participants_count) if cost is not None else None
        return {
            'reservation_id': self.reservation_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'booked_at': self.booked_at.isoformat(),
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'participants_count': self.participants_count,
            'is_cancelled': self.is_cancelled,
            'is_paid': self.is_paid,
            'excursion_title': (
                self.session.event.title
                if self.session and self.session.event else None
            ),
            'place': (
                self.session.event.place
                if self.session and self.session.event else None
            ),
            'total_cost': total,
            'payment_status': (
                self.payment.status
                if self.payment else 'unpaid'
            )
        }

    def to_dict_detailed(self):
        cost = float(self.session.cost) if self.session and self.session.cost is not None else None
        total = float(cost * self.participants_count) if cost is not None else None
        return {
            'reservation_id': self.reservation_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'booked_at': self.booked_at.isoformat(),
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'participants_count': self.participants_count,
            'is_cancelled': self.is_cancelled,
            'is_paid': self.is_paid,
            'excursion_title': (
                self.session.event.title
                if self.session and self.session.event else None
            ),
            'session_start_datetime': (
                self.session.start_datetime.isoformat()
                if self.session else None
            ),
            'place': (
                self.session.event.place
                if self.session and self.session.event else None
            ),
            'total_cost': total,
            'payment_status': (
                self.payment.status
                if self.payment else 'unpaid'
            )
        }


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.String(100), primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.reservation_id'), nullable=True)

    session_id = db.Column(db.Integer, db.ForeignKey('event_sessions.session_id'), nullable=True)
    participants_count = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='RUB')
    status = db.Column(db.String(50), nullable=False, default='pending')
    method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    reservation = db.relationship("Reservation", back_populates="payment", uselist=False)
    session = db.relationship("EventSession", back_populates="payments")


class Tag(db.Model):
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    events = db.relationship("Event", secondary=event_tags, back_populates="tags", lazy='subquery')

    def __str__(self):
        return f"Tag(id={self.tag_id}, name={self.name})"

    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'name': self.name,
        }
