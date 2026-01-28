from backend.core import db


class CompanyProject(db.Model):
    __tablename__ = 'company_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'order_index': self.order_index,
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
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'photo': self.photo,
            'text': self.text,
            'order_index': self.order_index
        }


class Partner(db.Model):
    __tablename__ = 'partner'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(500), nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'link': self.link,
            'order_index': self.order_index
        }


class Requisite(db.Model):
    __tablename__ = 'requisite'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    file = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'file': self.file
        }
