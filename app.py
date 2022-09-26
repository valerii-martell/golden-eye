"""Application's entry point module."""

import logging
from logging.config import dictConfig

from flask.logging import default_handler
from flask import Flask

import models
import tasks
from config import LOGGING

dictConfig(LOGGING)
app = Flask(__name__)

# Views importing should be after initialization
# of the application to make app variable visible
# within views module
import views

models.start_db()

app.logger = logging.getLogger('GoldenEye')
app.logger.removeHandler(default_handler)

# Entry point
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
