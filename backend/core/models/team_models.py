from backend.core import db


class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    team_lead_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    team_lead = db.relationship('User', foreign_keys=[team_lead_id])

    members = db.relationship('User', secondary='team_members', backref='teams')

    def __repr__(self):
        return f"<Team {self.team_name}>"

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "description": self.description,
            "team_lead": {
                "user_id": self.team_lead.user_id,
                "username": self.team_lead.username,
                "full_name": self.team_lead.full_name
            } if self.team_lead else None,
            "members": [
                {
                    "user_id": member.user_id,
                    "username": member.username,
                    "full_name": member.full_name
                } for member in self.members
            ],
            "cases": [
                case.case_name for case in self.cases  # Добавляем названия кейсов
            ]
        }


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)


from backend.core import db


class TeamCase(db.Model):
    __tablename__ = 'team_cases'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))  # фикс тут
    case_id = db.Column(db.Integer, db.ForeignKey('hackathon_cases.case_id'))
