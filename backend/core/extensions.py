from flask_jwt_extended import JWTManager
from flask_restx import Api

api = Api(security='BearerAuth', title="uknoAPI", description="API для сайта ukno")
api.authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'name': 'Authorization',
        'in': 'header',
    }
}
api.security = [{'Bearer': []}]
jwt = JWTManager()
