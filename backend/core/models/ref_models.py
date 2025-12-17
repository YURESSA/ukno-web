from backend.core import db


class CompanyProject(db.Model):
    __tablename__ = 'company_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
        }


class TrustReason(db.Model):
    __tablename__ = 'trust_reasons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }


class CompanyHistory(db.Model):
    __tablename__ = 'company_history'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(500), nullable=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'link': self.link,
            'title': self.title,
            'date': self.date.isoformat(),
            'description': self.description
        }


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'photo': self.photo,
            'full_name': self.full_name,
            'description': self.description
        }


class CulturalSpace(db.Model):
    __tablename__ = 'cultural_space'

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(255), nullable=True)
    text = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'photo': self.photo,
            'text': self.text
        }
