from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import CompanyProject
from backend.core.services.ref_service.company_project_service import get_all_projects, create_project, \
    get_project_by_id, update_project, delete_project

project_model = ref_ns.model('CompanyProject', {
    'title': fields.String(required=True, description='Название проекта'),
    'link': fields.String(required=True, description='Ссылка на проект'),
})


@ref_ns.route('/projects')
class ProjectList(Resource):

    @ref_ns.doc(description="Список всех проектов компании")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех проектов компании.

        **Ответ:**
            200 OK: Список объектов CompanyProject
            [
                {
                    "id": 1,
                    "title": "Проект 1",
                    "link": "https://example.com/project1"
                },
                ...
            ]
        """
        projects = get_all_projects()
        return [p.to_dict() for p in projects], 200

    @admin_required
    @ref_ns.expect(project_model)
    @ref_ns.doc(description="Создание нового проекта компании")
    def post(self) -> tuple[dict, int]:
        """
        Создание нового проекта компании.

        JSON body:
            title (str): Название проекта (обязательно)
            link (str): Ссылка на проект (обязательно)

        **Ответы:**
            201 Created: Возвращает созданный проект
            400 Bad Request: Ошибка валидации полей
        """
        data = request.json or {}
        try:
            project = create_project(
                title=data.get('title'),
                link=data.get('link')
            )
        except ValueError as e:
            return {'message': str(e)}, 400

        return project.to_dict(), 201


@ref_ns.route('/projects/<int:id>')
class ProjectResource(Resource):

    @ref_ns.doc(description="Получение проекта компании по ID")
    def get(self, id: int) -> tuple[dict, int]:
        """
        Получение проекта компании по его ID.

        Параметры:
            id (int): ID проекта

        **Ответы:**
            200 OK: Возвращает объект проекта
            404 Not Found: Если проект с указанным ID не найден
        """
        project = get_project_by_id(id)
        if not project:
            return {'message': 'Проект не найден'}, 404
        return project.to_dict(), 200

    @admin_required
    @ref_ns.expect(project_model)
    @ref_ns.doc(description="Обновление проекта компании по ID")
    def put(self, id: int) -> tuple[dict, int]:
        """
        Обновление проекта компании по его ID.

        Параметры:
            id (int): ID проекта

        JSON body:
            title (str): Название проекта (обязательно)
            link (str): Ссылка на проект (обязательно)

        **Ответы:**
            200 OK: Возвращает обновлённый проект
            400 Bad Request: Ошибка валидации полей
            404 Not Found: Если проект с указанным ID не найден
        """
        project = get_project_by_id(id)
        if not project:
            return {'message': 'Проект не найден'}, 404

        data = request.json or {}
        try:
            project = update_project(
                project,
                title=data.get('title'),
                link=data.get('link')
            )
        except ValueError as e:
            return {'message': str(e)}, 400

        return project.to_dict(), 200

    @admin_required
    @ref_ns.doc(description="Удаление проекта компании по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление проекта компании по ID.

        Параметры:
            id (int): ID проекта

        **Ответы:**
            200 OK: {"message": "Проект удалён"}
            404 Not Found: Если проект с указанным ID не найден
        """
        project = get_project_by_id(id)
        if not project:
            return {'message': 'Проект не найден'}, 404

        delete_project(project)
        return {'message': 'Проект удалён'}, 200
