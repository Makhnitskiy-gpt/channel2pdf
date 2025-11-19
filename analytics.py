"""
Модуль аналитики для отслеживания событий в приложении Channel2PDF.

Обеспечивает:
- Внутреннее логирование событий (export_started, export_success, export_failed, и т.д.)
- Сбор метрик без раскрытия чувствительных данных
- Возможность интеграции с внешними счётчиками через ANALYTICS_SNIPPET
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
import hashlib


# ============================================================================
# НАСТРОЙКА ЛОГГЕРА
# ============================================================================

# Создаём отдельный логгер для аналитики
analytics_logger = logging.getLogger('analytics')
analytics_logger.setLevel(logging.INFO)

# Формат для вывода JSON-строк
formatter = logging.Formatter('%(message)s')

# Хэндлер для записи в файл (или можно использовать общий server.log)
file_handler = logging.FileHandler('server.log', encoding='utf-8')
file_handler.setFormatter(formatter)
analytics_logger.addHandler(file_handler)

# Отключаем propagation, чтобы избежать дублирования в основном логе
analytics_logger.propagate = False


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def _hash_ip(ip: str) -> str:
    """
    Хэширует IP-адрес для приватности.

    Используется SHA-256 для необратимого преобразования IP,
    чтобы избежать хранения реальных IP-адресов.

    Args:
        ip: IP-адрес клиента

    Returns:
        str: Первые 16 символов SHA-256 хэша IP
    """
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def _get_client_ip(request: Request) -> str:
    """
    Получает IP-адрес клиента с учётом прокси.

    Проверяет заголовки X-Forwarded-For и X-Real-IP,
    которые используются при работе через прокси/CDN.

    Args:
        request: FastAPI Request объект

    Returns:
        str: IP-адрес клиента (хэшированный для приватности)
    """
    # Проверяем заголовки прокси
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        # X-Forwarded-For может содержать несколько IP через запятую,
        # берём первый (оригинальный клиентский IP)
        ip = forwarded_for.split(',')[0].strip()
        return _hash_ip(ip)

    real_ip = request.headers.get('x-real-ip')
    if real_ip:
        return _hash_ip(real_ip)

    # Fallback на стандартный client.host
    client_ip = request.client.host if request.client else "unknown"
    return _hash_ip(client_ip) if client_ip != "unknown" else "unknown"


def _get_user_agent(request: Request) -> str:
    """
    Получает User-Agent клиента, обрезая до разумной длины.

    Args:
        request: FastAPI Request объект

    Returns:
        str: User-Agent, обрезанный до 200 символов
    """
    user_agent = request.headers.get('user-agent', 'unknown')
    # Обрезаем до 200 символов для экономии места
    return user_agent[:200] if len(user_agent) > 200 else user_agent


def _get_language(request: Request) -> str:
    """
    Определяет язык интерфейса из cookies.

    Args:
        request: FastAPI Request объект

    Returns:
        str: Код языка ('ru' или 'en'), по умолчанию 'ru'
    """
    lang = request.cookies.get('channel2pdf_language', 'ru')
    # Валидация языка
    return lang if lang in ['ru', 'en'] else 'ru'


# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ ЛОГИРОВАНИЯ СОБЫТИЙ
# ============================================================================

def log_event(
    event_type: str,
    request: Request,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Логирует аналитическое событие в формате JSON.

    Собирает контекстную информацию о запросе и записывает событие
    в лог для последующего анализа.

    Args:
        event_type: Тип события (export_started, export_success, export_failed, etc.)
        request: FastAPI Request объект
        extra: Дополнительные данные для логирования (опционально)

    События:
        - page_view: Просмотр главной страницы
        - export_started: Начало генерации PDF
        - export_success: Успешная генерация PDF
        - export_failed: Ошибка при генерации PDF
        - lang_changed: Переключение языка

    Пример использования:
        log_event(
            "export_started",
            request,
            extra={
                "channel_input": "@durov",
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "lang": "ru"
            }
        )

    Предостережения:
        - НЕ передавайте в extra чувствительные данные (токены, пароли)
        - НЕ передавайте полный текст постов
        - НЕ передавайте полные traceback (только короткий error_type)
    """
    # Формируем базовую структуру события
    event_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",  # ISO 8601 формат с UTC
        "event_type": event_type,
        "path": str(request.url.path),
        "lang": _get_language(request),
        "client_ip_hash": _get_client_ip(request),  # Хэшированный IP для приватности
        "user_agent": _get_user_agent(request)
    }

    # Добавляем дополнительные данные, если переданы
    if extra:
        # Фильтруем и безопасно добавляем extra данные
        # (можно добавить дополнительную валидацию при необходимости)
        event_data["extra"] = extra

    # Логируем событие как одну JSON-строку
    analytics_logger.info(json.dumps(event_data, ensure_ascii=False))


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЧАСТО ИСПОЛЬЗУЕМЫХ СОБЫТИЙ
# ============================================================================

def log_page_view(request: Request) -> None:
    """
    Логирует просмотр главной страницы.

    Args:
        request: FastAPI Request объект
    """
    log_event(
        "page_view",
        request,
        extra={"lang": _get_language(request)}
    )


def log_export_started(
    request: Request,
    channel_input: str,
    date_from: str,
    date_to: str
) -> None:
    """
    Логирует начало экспорта канала.

    Args:
        request: FastAPI Request объект
        channel_input: Введённое название канала (без токенов!)
        date_from: Дата начала периода
        date_to: Дата окончания периода
    """
    log_event(
        "export_started",
        request,
        extra={
            # Сохраняем только первые 100 символов для безопасности
            "channel_input": channel_input[:100] if len(channel_input) > 100 else channel_input,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "lang": _get_language(request)
        }
    )


def log_export_success(
    request: Request,
    channel_input: str,
    posts_count: Optional[int] = None
) -> None:
    """
    Логирует успешное завершение экспорта.

    Args:
        request: FastAPI Request объект
        channel_input: Введённое название канала
        posts_count: Количество обработанных постов (опционально)
    """
    extra_data = {
        "channel_input": channel_input[:100] if len(channel_input) > 100 else channel_input,
        "lang": _get_language(request)
    }

    if posts_count is not None:
        extra_data["posts_count"] = posts_count

    log_event("export_success", request, extra=extra_data)


def log_export_failed(
    request: Request,
    channel_input: str,
    error_type: str
) -> None:
    """
    Логирует ошибку при экспорте.

    Args:
        request: FastAPI Request объект
        channel_input: Введённое название канала
        error_type: Тип ошибки (короткое описание, НЕ полный traceback)
    """
    log_event(
        "export_failed",
        request,
        extra={
            "channel_input": channel_input[:100] if len(channel_input) > 100 else channel_input,
            "error_type": error_type[:200] if len(error_type) > 200 else error_type,
            "lang": _get_language(request)
        }
    )


def log_lang_changed(
    request: Request,
    new_lang: str
) -> None:
    """
    Логирует переключение языка интерфейса.

    Args:
        request: FastAPI Request объект
        new_lang: Новый выбранный язык
    """
    log_event(
        "lang_changed",
        request,
        extra={"new_lang": new_lang}
    )


# ============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    """
    Примеры использования модуля аналитики.
    Этот блок выполняется только при прямом запуске: python analytics.py
    """
    print("=" * 60)
    print("МОДУЛЬ АНАЛИТИКИ CHANNEL2PDF")
    print("=" * 60)
    print("\nДоступные функции для логирования событий:\n")

    print("1. log_event(event_type, request, extra=None)")
    print("   - Базовая функция логирования произвольных событий\n")

    print("2. log_page_view(request)")
    print("   - Просмотр главной страницы\n")

    print("3. log_export_started(request, channel_input, date_from, date_to)")
    print("   - Начало генерации PDF\n")

    print("4. log_export_success(request, channel_input, posts_count=None)")
    print("   - Успешная генерация PDF\n")

    print("5. log_export_failed(request, channel_input, error_type)")
    print("   - Ошибка при генерации PDF\n")

    print("6. log_lang_changed(request, new_lang)")
    print("   - Переключение языка\n")

    print("=" * 60)
    print("События записываются в server.log в формате JSON")
    print("=" * 60)
