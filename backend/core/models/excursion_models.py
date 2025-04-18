from datetime import datetime
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


class EventType(db.Model):
    __tablename__ = 'event_types'

    event_type_id = db.Column(db.Integer, primary_key=True)
    event_type_name = db.Column(db.String(255), nullable=False)

    excursions = db.relationship("Excursion", back_populates="event_type", lazy=True)

    def __str__(self):
        return f"EventType(id={self.event_type_id}, name={self.event_type_name})"

    def to_dict(self):
        return {
            'event_type_id': self.event_type_id,
            'event_type_name': self.event_type_name
        }


class Excursion(db.Model):
    __tablename__ = 'excursions'

    excursion_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_types.event_type_id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    category = db.relationship("Category", back_populates="excursions")
    event_type = db.relationship("EventType", back_populates="excursions")
    photos = db.relationship("ExcursionPhoto", back_populates="excursion", cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship("ExcursionSession", back_populates="excursion", cascade="all, delete-orphan", lazy=True)
    recurring_schedules = db.relationship("RecurringSchedule", back_populates="excursion", cascade="all, delete-orphan",
                                          lazy=True)
    tags = db.relationship("Tag", secondary=excursion_tags, back_populates="excursions", lazy='subquery')

    def __str__(self):
        return f"Excursion(id={self.excursion_id}, title={self.title}, description={self.description}, " \
               f"duration={self.duration}, category_id={self.category_id}, event_type_id={self.event_type_id}, " \
               f"created_by={self.created_by}, is_active={self.is_active})"

    def to_dict(self):
        return {
            'excursion_id': self.excursion_id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'category': self.category.to_dict() if self.category else None,
            'event_type': self.event_type.to_dict() if self.event_type else None,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'photos': [photo.to_dict() for photo in self.photos],
            'sessions': [session.to_dict() for session in self.sessions],
            'recurring_schedules': [schedule.to_dict() for schedule in self.recurring_schedules],
            'tags': [tag.to_dict() for tag in self.tags]
        }


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

    def __str__(self):
        return f"ExcursionSession(id={self.session_id}, excursion_id={self.excursion_id}, " \
               f"start_datetime={self.start_datetime}, max_participants={self.max_participants}, " \
               f"cost={self.cost})"

    def to_dict(self):
        return {
            'start_datetime': self.start_datetime.isoformat(),
            'max_participants': self.max_participants,
            'cost': str(self.cost)
        }


class RecurringSchedule(db.Model):
    __tablename__ = 'recurring_schedules'

    recurring_id = db.Column(db.Integer, primary_key=True)
    excursion_id = db.Column(db.Integer, db.ForeignKey('excursions.excursion_id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0 = воскресенье, 6 = суббота
    start_time = db.Column(db.Time, nullable=False)
    count_of_repeats = db.Column(db.Integer, nullable=False, default=0)
    repeats = db.Column(db.Integer, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)

    excursion = db.relationship("Excursion", back_populates="recurring_schedules")

    def __str__(self):
        return f"RecurringSchedule(id={self.recurring_id}, excursion_id={self.excursion_id}, " \
               f"weekday={self.weekday}, start_time={self.start_time}, count_of_repeats={self.count_of_repeats}, " \
               f"repeats={self.repeats}, max_participants={self.max_participants})"

    def to_dict(self):
        return {
            'weekday': self.weekday,
            'start_time': self.start_time.isoformat(),
            'count_of_repeats': self.count_of_repeats,
            'repeats': self.repeats,
            'max_participants': self.max_participants
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
