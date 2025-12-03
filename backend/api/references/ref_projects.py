from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import CompanyProject

project_model = ref_ns.model('CompanyProject', {
    'title': fields.String(required=True, description='Название проекта'),
    'description': fields.String(required=False, description='Описание проекта'),
})


@ref_ns.route('/projects')
class ProjectList(Resource):

    @ref_ns.doc(description="Список всех проектов компании")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех проектов компании.

        Returns:
            list[dict]: Список проектов.
        """
        projects = CompanyProject.query.all()
        return [p.to_dict() for p in projects], 200

    @admin_required
    @ref_ns.expect(project_model)
    @ref_ns.doc(description="Создание нового проекта компании")
    def post(self) -> tuple[dict, int]:
        """
        Создание нового проекта компании.

        JSON body:
            title (str): Название проекта (обязательно).
            description (str): Описание проекта.

        """
        data = request.json or {}

        title = data.get('title')
        if not title:
            return {'message': 'Поле title обязательно'}, 400

        project = CompanyProject(
            title=title,
            description=data.get('description')
        )

        db.session.add(project)
        db.session.commit()

        return project.to_dict(), 201


@ref_ns.route('/projects/<int:id>')
class ProjectResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление проекта компании по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление проекта компании по ID.
        """
        project = CompanyProject.query.get(id)
        if not project:
            return {'message': 'Проект не найден'}, 404

        db.session.delete(project)
        db.session.commit()

        return {'message': 'Проект удалён'}, 200
