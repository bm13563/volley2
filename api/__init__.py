from flask import Flask
from dotenv import load_dotenv

from common.logging import get_logger
from api.db import DbManager


logger = get_logger()


load_dotenv()
app = Flask(__name__)
logger.info("starting application")

db = DbManager()


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"
