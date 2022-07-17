import logging


DB_PATH = "data/golden-eye.db"
LOGS_DB_PATH = "data/golden-eye-logs.db"

HTTP_TIMEOUT = 15

IP_LIST = ["127.0.0.1", "127.0.0.10"]

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] [%(levelname)s] - %(name)s: %(message)s",
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'app.log',
        },
    },
    'loggers': {
        'GoldenEye': {
            'handlers': ['file'],
            'level': logging.DEBUG
        },
        'Api': {
            'handlers': ['file'],
            'level': logging.DEBUG
        },
        'Tasks': {
            'handlers': ['file', 'console'],
            'level': logging.DEBUG
        },
    },
}