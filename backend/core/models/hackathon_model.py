from sqlalchemy import Column, Integer, String, Text

from backend.core import db


class HackathonCase(db.Model):
    __tablename__ = 'hackathon_cases'
    case_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    original_filename = Column(String(255), nullable=True)

    cases = db.relationship("HackathonCase", secondary="team_cases", backref="teams")

    def __repr__(self):
        return f"<HackathonCase {self.title}>"

    def to_dict(self):
        """Преобразовать объект кейса в словарь."""
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
            "original_filename": self.original_filename  # Добавляем оригинальное имя файла
        }
