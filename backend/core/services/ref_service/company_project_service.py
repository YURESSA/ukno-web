from backend.core import db
from backend.core.models.ref_models import CompanyProject


def get_all_projects():
    return CompanyProject.query.all()


def get_project_by_id(project_id: int) -> CompanyProject | None:
    return CompanyProject.query.get(project_id)


def create_project(title: str, link: str) -> CompanyProject:
    if not title:
        raise ValueError('Поле title обязательно')
    if not link:
        raise ValueError('Поле link обязательно')

    project = CompanyProject(title=title, link=link)
    db.session.add(project)
    db.session.commit()
    return project


def update_project(project: CompanyProject, title: str, link: str) -> CompanyProject:
    if not title:
        raise ValueError('Поле title обязательно')
    if not link:
        raise ValueError('Поле link обязательно')

    project.title = title
    project.link = link
    db.session.commit()
    return project


def delete_project(project: CompanyProject):
    db.session.delete(project)
    db.session.commit()
