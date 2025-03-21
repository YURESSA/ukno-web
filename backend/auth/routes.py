from http import HTTPStatus

from flasgger import swag_from
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import auth_bp
from .services import *


@auth_bp.route("/register", methods=["POST"])
@swag_from("docs/register.yml")
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    new_user = create_user(username, email, password)

    if not new_user:
        return jsonify({"message": "User with this username or email already exists"}), HTTPStatus.CONFLICT

    return jsonify({"message": "User created successfully"}), HTTPStatus.CREATED


@auth_bp.route("/login", methods=["POST"])
@swag_from("docs/login.yml")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    access_token = authenticate_user(username, password)

    if access_token:
        return jsonify(access_token=access_token), HTTPStatus.OK

    return jsonify({"message": "Invalid credentials"}), HTTPStatus.UNAUTHORIZED


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
@swag_from("docs/protected.yml")
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello, {current_user}!"}), HTTPStatus.OK
