from logging import StreamHandler, getLogger

from flask import Flask
from dotenv import load_dotenv

from api.logging import CustomFormatter
from api.db import DbManager


logger = getLogger(__name__)
log_handler = StreamHandler()
log_handler.setFormatter(CustomFormatter())
logger.addHandler(log_handler)

load_dotenv()

app = Flask(__name__)

app.logger.info("started flask server")

app.db = DbManager()
