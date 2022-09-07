from logging import StreamHandler
from flask import Flask

from api.logging import CustomFormatter


app = Flask(__name__)

log_handler = StreamHandler()
log_handler.setFormatter(CustomFormatter())
app.logger.addHandler(log_handler)
del app.logger.handlers[0] # Remove the default handler

app.logger.info("started flask server")
