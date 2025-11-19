"""
Бизнес-логика для генерации отчётов.
Этот модуль инкапсулирует основную логику работы с Telegram и PDF,
чтобы её можно было использовать как из CLI, так и из веб-интерфейса.
"""

import asyncio
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import os

import config
from telegram_client import get_client
from fetch_posts import fetch_posts, sort_posts, get_demo_posts
from pdf_builder import create_pdf


class ReportGenerationError(Exception):
    """Базовое исключение для ошибок генерации отчёта."""
    pass


class ChannelNotFoundError(ReportGenerationError):
    """Канал не найден или недоступен."""
    pass


class NoPostsFoundError(ReportGenerationError):
    """Постов за указанный период не найдено."""
    pass


class TelegramConnectionError(ReportGenerationError):
    """Ошибка подключения к Telegram."""
    pass


def is_demo_mode():
    """
    Проверяет, нужно ли использовать демо-режим.

    Returns:
        bool: True, если демо-режим активен
    """
    if getattr(config, 'DEMO_MODE', False):
        return True

    if config.API_ID is None or config.API_ID == 0:
        return True

    if config.API_HASH is None or config.API_HASH == "":
        return True

    return False


async def generate_report(
    channel: str,
    date_from: date,
    date_to: date,
    sort_type: str,  # 'date' | 'reactions' | 'views'
    ascending: bool,
    filename: Optional[str] = None,
    output_dir: str = "generated"
) -> Path:
    """
    Генерирует PDF-отчёт с постами из Telegram-канала.

    Args:
        channel: Username канала (с @ или без) или ссылка
        date_from: Начало периода
        date_to: Конец периода
        sort_type: Тип сортировки ('date', 'reactions', 'views')
        ascending: True для возрастания, False для убывания
        filename: Имя PDF-файла (опционально). Если не указано, генерируется автоматически.
        output_dir: Директория для сохранения PDF (по умолчанию "generated")

    Returns:
        Path: Полный путь к сгенерированному PDF-файлу

    Raises:
        ChannelNotFoundError: Если канал не найден или недоступен
        NoPostsFoundError: Если постов за указанный период не найдено
        TelegramConnectionError: Если не удалось подключиться к Telegram
        ReportGenerationError: Другие ошибки генерации отчёта
        ValueError: Неверные параметры (даты, тип сортировки и т.п.)
    """
    # Валидация параметров
    if not channel or not channel.strip():
        raise ValueError("Канал не может быть пустым")

    if date_to < date_from:
        raise ValueError("Дата окончания не может быть раньше даты начала")

    if sort_type not in ['date', 'reactions', 'views']:
        raise ValueError(f"Неверный тип сортировки: {sort_type}. Допустимые значения: date, reactions, views")

    # Создаём директорию для PDF, если её нет
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Генерируем имя файла, если не указано
    if not filename:
        clean_channel = channel.replace('@', '').replace('/', '_').replace('\\', '_')
        filename = f"{clean_channel}_{date_from}_{date_to}.pdf"

    # Добавляем расширение .pdf, если его нет
    if not filename.endswith('.pdf'):
        filename += '.pdf'

    # Полный путь к файлу
    pdf_path = output_path / filename

    # Проверяем режим работы
    demo_mode = is_demo_mode()

    try:
        if demo_mode:
            # Демо-режим: используем мок-данные
            posts = get_demo_posts(date_from, date_to)
        else:
            # Обычный режим: подключаемся к Telegram
            try:
                client = await get_client()
            except Exception as e:
                raise TelegramConnectionError(f"Не удалось подключиться к Telegram: {str(e)}")

            try:
                # Получаем посты из канала
                posts = await fetch_posts(channel, date_from, date_to, client)
            except ValueError as e:
                # Ошибка получения канала
                await client.disconnect()
                raise ChannelNotFoundError(str(e))
            except Exception as e:
                await client.disconnect()
                raise ReportGenerationError(f"Ошибка получения постов: {str(e)}")
            finally:
                # Всегда отключаемся от Telegram
                try:
                    await client.disconnect()
                except:
                    pass

        # Проверяем, что посты найдены
        if not posts:
            raise NoPostsFoundError(f"Постов за период с {date_from} по {date_to} не найдено")

        # Сортируем посты
        try:
            sorted_posts = sort_posts(posts, sort_type, ascending)
        except Exception as e:
            raise ReportGenerationError(f"Ошибка сортировки постов: {str(e)}")

        # Создаём PDF
        try:
            pdf_path_str = create_pdf(sorted_posts, str(pdf_path), channel)
            return Path(pdf_path_str)
        except Exception as e:
            raise ReportGenerationError(f"Ошибка создания PDF: {str(e)}")

    except (ChannelNotFoundError, NoPostsFoundError, TelegramConnectionError, ReportGenerationError, ValueError):
        # Пробрасываем наши исключения дальше
        raise
    except Exception as e:
        # Все остальные ошибки оборачиваем в ReportGenerationError
        raise ReportGenerationError(f"Неожиданная ошибка: {str(e)}")


# Вспомогательная синхронная обёртка для использования в синхронном коде (CLI)
def generate_report_sync(
    channel: str,
    date_from: date,
    date_to: date,
    sort_type: str,
    ascending: bool,
    filename: Optional[str] = None,
    output_dir: str = "generated"
) -> Path:
    """
    Синхронная версия generate_report для использования в синхронном коде (CLI).
    Параметры и возвращаемое значение аналогичны асинхронной версии.

    ВАЖНО: Эта функция создаёт новый event loop с помощью asyncio.run().
    НЕ используйте её из асинхронного контекста (FastAPI, aiohttp и т.п.) -
    там используйте напрямую await generate_report().
    """
    return asyncio.run(generate_report(
        channel, date_from, date_to, sort_type, ascending, filename, output_dir
    ))
