#!/bin/bash

# Скрипт для запуска веб-сервера FastAPI

# Переход в директорию проекта
cd "/Users/danil/VS Code"

# Активация виртуального окружения
source venv/bin/activate

# Запуск uvicorn сервера
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000
