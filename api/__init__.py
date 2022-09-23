from os import getcwd

from flask import Flask
from dotenv import load_dotenv
load_dotenv(str(getcwd()) + "/dev.env")

from common.logging import get_logger
from api.db.db_manager import DbManager
from api.resources.auth import auth
from api.resources.auth.auth_utils import token_required


logger = get_logger()

app = Flask(__name__)
dbm = DbManager()
logger.info("starting application")

app.register_blueprint(auth)
logger.info("registered auth blueprint")


@app.route("/ping", methods=["GET"])
def ping():
    return {
        "status_code": 200,
        "message": "pong",
        "data": {},
    }


@app.route("/protected_ping", methods=["GET"])
@token_required
def protected_ping():
    return {
        "status_code": 200,
        "message": "protected pong",
        "data": {},
    }