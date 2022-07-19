import logging
from logging.config import dictConfig

from flask.logging import default_handler
from flask import Flask

import models
from config import LOGGING

dictConfig(LOGGING)
app = Flask(__name__)

import views

models.start_db()

app.logger = logging.getLogger('GoldenEye')
app.logger.removeHandler(default_handler)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
