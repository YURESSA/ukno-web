from datetime import datetime

from backend.core import db


class NewsImage(db.Model):
    __tablename__ = 'news_images'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.news_id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    news = db.relationship('News', back_populates='images')


class News(db.Model):
    __tablename__ = 'news'

    news_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Автор новости (связь с User)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    author = db.relationship('User', foreign_keys=[author_id], backref='news')
    photo_author = db.Column(db.String(200), nullable=True)

    images = db.relationship('NewsImage', back_populates='news', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            "news_id": self.news_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "images": [image.image_path for image in self.images],
            "author": {
                "user_id": self.author.user_id,
                "full_name": self.author.full_name,
                "email": self.author.email
            },
            "photo_author": self.photo_author
        }
