#!/bin/sh

sleep 10

poetry run alembic upgrade head
poetry run uvicorn --host 0.0.0.0 --port 8000 app.app:app --reload
