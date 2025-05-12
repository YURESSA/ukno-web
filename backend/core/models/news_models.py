from datetime import datetime

from backend.core import db


class News(db.Model):
    __tablename__ = 'news'

    news_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    author = db.relationship('User', backref=db.backref('news', lazy=True))

    def __repr__(self):
        return f"<News {self.title}>"

    def to_dict(self):
        return {
            "news_id": self.news_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "image_path": self.image_path,
            "author": {
                "user_id": self.author.user_id,
                "full_name": self.author.full_name,
                "username": self.author.username
            }
        }
