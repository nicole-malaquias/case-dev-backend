#!/bin/sh

# Adicione um pequeno atraso para garantir que o banco de dados esteja pronto
sleep 10

poetry run alembic upgrade head
poetry run uvicorn --host 0.0.0.0 --port 8000 app.app:app