from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

from backend.core import db
from backend.core.models.auth_models import User
from backend.core.models.team_models import Team


def create_team(data):
    team_name = data.get("team_name")
    description = data.get("description")
    team_lead_id = data.get("team_lead_id")

    new_team = Team(team_name=team_name, description=description, team_lead_id=team_lead_id)

    team_lead = User.query.get(team_lead_id)

    if not team_lead:
        return {"message": "Тимлид не найден."}, HTTPStatus.NOT_FOUND

    new_team.members.append(team_lead)

    try:
        db.session.add(new_team)
        db.session.commit()
        return {"message": "Команда успешно создана."}, HTTPStatus.CREATED
    except IntegrityError:
        db.session.rollback()
        return {"message": "Команда с таким названием уже существует."}, HTTPStatus.BAD_REQUEST


def add_member_to_team(team_id, user_id):
    team = Team.query.get(team_id)
    user = User.query.get(user_id)

    if not team or not user:
        return {"message": "Команда или пользователь не найдены."}, 404

    if user in team.members:
        return {"message": "Пользователь уже состоит в этой команде."}, 200

    team.members.append(user)
    db.session.commit()

    return {"message": "Пользователь успешно добавлен в команду."}, 200


def get_team_members(team_id):
    team = Team.query.get(team_id)
    if not team:
        return None
    return team.members
