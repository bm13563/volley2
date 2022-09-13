from flask import abort, request, jsonify, Blueprint

from api.resources.auth.auth_controller import register_controller, login_controller
from common.logging import get_logger


logger = get_logger()


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    username = request_data.get("username", False)
    hashed_password = request_data.get("password", False)

    if not username or not hashed_password:
        abort(400, "username and password are required")

    register_controller()

    return jsonify({"status_code": 200, "message": "user registered", "data": {}})


@auth.route("/login", methods=["POST"])
def login():
    request_data = request.get_json()
    username = request_data.get("username", False)
    hashed_password = request_data.get("password", False)

    if not username or not hashed_password:
        abort(400, "username and password are required")

    token = login_controller(username, hashed_password)

    return jsonify(
        {
            "status_code": 200,
            "message": "user authenticated",
            "data": {"token": token.decode("utf-8")},
        }
    )
