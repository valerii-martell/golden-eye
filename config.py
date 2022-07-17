import logging


DB_PATH = "data/golden-eye.db"
LOGS_DB_PATH = "data/golden-eye-logs.db"

LOGGER_CONFIG = dict(level=logging.DEBUG,
                     file="app.log",
                     formatter=logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s : %(message)s")
                     )

HTTP_TIMEOUT = 15

IP_LIST = ["127.0.0.1", "127.0.0.10"]