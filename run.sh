#!/bin/bash

exec python3 tasks.py &
exec gunicorn -w 4 --bind 0.0.0.0:$PORT app:app
