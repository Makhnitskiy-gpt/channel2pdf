"""
Веб-приложение для парсинга Telegram-каналов на FastAPI.
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import os

from core_service import (
    generate_report,
    ReportGenerationError,
    ChannelNotFoundError,
    NoPostsFoundError,
    TelegramConnectionError,
    is_demo_mode
)

# Импортируем конфигурацию аналитики
from config import ANALYTICS_SNIPPET

# Импортируем модуль аналитики
from analytics import (
    log_export_started,
    log_export_success,
    log_export_failed
)

# Импортируем парсер логов для страницы админки
from log_parser import parse_log_file

# Импортируем переменную окружения для ограничения доступа
from config import ENV


# Создаём приложение
app = FastAPI(
    title="Telegram Channel Parser",
    description="Веб-интерфейс для парсинга Telegram-каналов и генерации PDF-отчётов",
    version="1.0.0"
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="templates")

# Директория для сгенерированных PDF
GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Главная страница с формой для ввода параметров.
    """
    demo_mode = is_demo_mode()

    # Определяем язык из cookies или заголовков (по умолчанию ru)
    lang = request.cookies.get('channel2pdf_language', 'ru')
    if lang not in ['ru', 'en']:
        lang = 'ru'

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "demo_mode": demo_mode,
            "lang": lang,
            "analytics_snippet": ANALYTICS_SNIPPET  # Передаём сниппет внешнего счётчика
        }
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    channel: str = Form(...),
    date_from: str = Form(...),
    date_to: str = Form(...),
    sort_type: str = Form(...),
    direction: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Обрабатывает форму генерации отчёта.
    """
    demo_mode = is_demo_mode()

    # Определяем язык из cookies
    lang = request.cookies.get('channel2pdf_language', 'ru')
    if lang not in ['ru', 'en']:
        lang = 'ru'

    # Сохраняем введённые значения для возврата при ошибке
    form_data = {
        "channel": channel,
        "date_from": date_from,
        "date_to": date_to,
        "sort_type": sort_type,
        "direction": direction,
        "filename": filename or ""
    }

    # Валидация канала
    if not channel or not channel.strip():
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Канал не может быть пустым",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    # Валидация и парсинг дат
    try:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
    except ValueError:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Неверный формат даты начала. Используйте формат ГГГГ-ММ-ДД",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    try:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Неверный формат даты окончания. Используйте формат ГГГГ-ММ-ДД",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    # Проверка диапазона дат
    if date_to_obj < date_from_obj:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Дата окончания не может быть раньше даты начала",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    # Валидация типа сортировки
    if sort_type not in ['date', 'reactions', 'views']:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Неверный тип сортировки: {sort_type}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    # Валидация направления сортировки
    if direction not in ['asc', 'desc']:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Неверное направление сортировки: {direction}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    # Конвертируем направление в bool
    ascending = (direction == 'asc')

    # Логируем начало экспорта
    log_export_started(
        request=request,
        channel_input=channel.strip(),
        date_from=date_from,
        date_to=date_to
    )

    # Генерируем отчёт
    try:
        pdf_path = await generate_report(
            channel=channel.strip(),
            date_from=date_from_obj,
            date_to=date_to_obj,
            sort_type=sort_type,
            ascending=ascending,
            filename=filename.strip() if filename and filename.strip() else None,
            output_dir=str(GENERATED_DIR)
        )

        # Логируем успешное завершение экспорта
        # Примечание: количество постов можно добавить позже из результата генерации
        log_export_success(
            request=request,
            channel_input=channel.strip(),
            posts_count=None  # TODO: передать реальное количество постов из generate_report
        )

        # Формируем данные для страницы успеха
        sort_type_names = {
            'date': 'дате',
            'reactions': 'количеству реакций',
            'views': 'количеству просмотров'
        }
        direction_name = 'по возрастанию' if ascending else 'по убыванию'

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "success": True,
                "pdf_filename": pdf_path.name,
                "channel": channel,
                "date_from": date_from,
                "date_to": date_to,
                "sort_type_name": sort_type_names[sort_type],
                "direction_name": direction_name,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    except ChannelNotFoundError as e:
        # Логируем ошибку "Канал не найден"
        log_export_failed(
            request=request,
            channel_input=channel.strip(),
            error_type="ChannelNotFoundError"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Канал не найден: {str(e)}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    except NoPostsFoundError as e:
        # Логируем ошибку "Постов не найдено"
        log_export_failed(
            request=request,
            channel_input=channel.strip(),
            error_type="NoPostsFoundError"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e),
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    except TelegramConnectionError as e:
        # Логируем ошибку подключения к Telegram
        log_export_failed(
            request=request,
            channel_input=channel.strip(),
            error_type="TelegramConnectionError"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Ошибка подключения к Telegram: {str(e)}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    except ReportGenerationError as e:
        # Логируем ошибку генерации отчёта
        log_export_failed(
            request=request,
            channel_input=channel.strip(),
            error_type="ReportGenerationError"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Ошибка генерации отчёта: {str(e)}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )

    except Exception as e:
        # Логируем неожиданную ошибку
        log_export_failed(
            request=request,
            channel_input=channel.strip(),
            error_type=f"UnexpectedError: {type(e).__name__}"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Неожиданная ошибка: {str(e)}",
                "form_data": form_data,
                "demo_mode": demo_mode,
                "lang": lang,
                "analytics_snippet": ANALYTICS_SNIPPET
            }
        )


@app.get("/files/{filename}")
async def download_file(filename: str):
    """
    Скачивание сгенерированного PDF-файла.
    Защищено от обращения к файлам вне директории generated.
    """
    # Безопасная проверка имени файла
    # Запрещаем path traversal атаки
    if '/' in filename or '\\' in filename or '..' in filename:
        return HTMLResponse(
            content="<h1>403 Forbidden</h1><p>Недопустимое имя файла</p>",
            status_code=403
        )

    # Проверяем, что файл существует
    file_path = GENERATED_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        return HTMLResponse(
            content="<h1>404 Not Found</h1><p>Файл не найден</p>",
            status_code=404
        )

    # Проверяем, что файл действительно находится в нужной директории
    # (защита от symlink атак)
    try:
        file_path.resolve().relative_to(GENERATED_DIR.resolve())
    except ValueError:
        return HTMLResponse(
            content="<h1>403 Forbidden</h1><p>Доступ запрещён</p>",
            status_code=403
        )

    # Отдаём файл
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/pdf'
    )


@app.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request):
    """
    Страница аналитики для администратора (dev-only).

    ⚠️  ВАЖНО: В продакшене этот эндпоинт отключён.
    Для доступа в проде установите ENV != "production" или добавьте
    HTTP basic auth защиту.

    TODO: Добавить HTTP basic auth для доступа в проде
    TODO: Или использовать сессии/JWT токены для авторизации
    """
    # Ограничиваем доступ только для dev/staging окружения
    # В продакшене возвращаем 404
    if ENV == "production":
        return HTMLResponse(
            content="""
            <html>
                <head><title>404 Not Found</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>404 Not Found</h1>
                    <p>Страница не найдена</p>
                </body>
            </html>
            """,
            status_code=404
        )

    # Парсим логи
    analytics = parse_log_file("server.log")

    # Определяем язык из cookies
    lang = request.cookies.get('channel2pdf_language', 'ru')
    if lang not in ['ru', 'en']:
        lang = 'ru'

    # Подготавливаем данные для шаблона
    conversion_rate = analytics.get_conversion_rate()

    # Формируем статистику по дням (последние 30 дней)
    daily_stats = analytics.get_daily_stats_sorted(reverse=True)[:30]

    # Топ-10 каналов
    top_channels = analytics.top_channels.most_common(10)

    # Подготавливаем данные об ошибках
    errors_list = [
        {"error_type": error_type, "count": count}
        for error_type, count in analytics.errors_by_type.most_common()
    ]

    return templates.TemplateResponse(
        "admin_analytics.html",
        {
            "request": request,
            "lang": lang,
            "analytics": analytics,
            "conversion_rate": conversion_rate,
            "daily_stats": daily_stats,
            "top_channels": top_channels,
            "errors_list": errors_list,
            "env": ENV
        }
    )


@app.get("/health")
async def health():
    """
    Healthcheck эндпоинт для проверки работоспособности сервиса.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
