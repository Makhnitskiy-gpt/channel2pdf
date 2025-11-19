# Инструкция по установке

## Быстрый старт

### 1. Создайте виртуальное окружение

```bash
python3 -m venv venv
```

### 2. Активируйте виртуальное окружение

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте конфигурацию (опционально)

Если хотите работать с реальными каналами:

1. Откройте [config.py](config.py)
2. Заполните `API_ID` и `API_HASH` (получить на https://my.telegram.org/apps)
3. Установите `DEMO_MODE = False`

Для тестирования можно оставить `DEMO_MODE = True`.

## Запуск

### CLI-версия

```bash
python main.py
```

### Веб-версия

```bash
uvicorn web_app:app --reload
```

Или:

```bash
python web_app.py
```

Затем откройте в браузере: http://localhost:8000

## Деактивация виртуального окружения

Когда закончите работу:

```bash
deactivate
```

## Возможные проблемы

### Ошибка "externally-managed-environment"

Если при установке зависимостей без venv возникает эта ошибка - создайте виртуальное окружение (шаги 1-3).

### Ошибка "command not found: python"

Используйте `python3` вместо `python`:

```bash
python3 -m venv venv
python3 main.py
```
