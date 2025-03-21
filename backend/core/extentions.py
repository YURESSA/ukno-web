from flasgger import Swagger
from flask_jwt_extended import JWTManager

swagger = Swagger(template={
    "swagger": "2.0",
    "info": {
        "title": "UKNO API",
        "description": "API documentation",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "JWT": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Введите Bearer токен в формате `Bearer <your_token>`"
        }
    },
    "security": [{"Bearer": []}]
})

jwt = JWTManager()
