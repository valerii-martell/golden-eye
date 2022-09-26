"""This module contains all app's config variables."""

import logging
import os

KEYS = {
    'coinmarketcap_api': os.environ.get('COINMARKETCAP_API_KEY')
}

DB_CONN = {
    'database': os.environ.get('POSTGRESQL_DATABASE'),
    'database_logs': os.environ.get('POSTGRESQL_LOGS_DATABASE'),
    'host': os.environ.get('POSTGRESQL_HOST'),
    'user': os.environ.get('POSTGRESQL_USER'),
    'password': os.environ.get('POSTGRESQL_PASSWORD'),
    'port': os.environ.get('POSTGRESQL_PORT'),
    'sslmode': os.environ.get('POSTGRESQL_SSLMODE'),
}

DB_PATH = "data/golden-eye.db"
LOGS_DB_PATH = "data/golden-eye-logs.db"

JOBS_STORE = "data/jobs.db"

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
