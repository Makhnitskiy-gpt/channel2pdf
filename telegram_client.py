"""
Модуль для работы с Telegram клиентом.
"""

from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME


def validate_credentials():
    """Проверяет, что API_ID и API_HASH заполнены."""
    if API_ID is None or API_HASH is None:
        raise ValueError(
            "Ошибка: API_ID и API_HASH не заполнены.\n"
            "Откройте файл config.py и заполните эти значения.\n"
            "Получить их можно на https://my.telegram.org/apps"
        )


async def get_client():
    """
    Создаёт и возвращает подключённый Telegram клиент.

    Returns:
        TelegramClient: Подключённый клиент

    Raises:
        ValueError: Если API_ID или API_HASH не заполнены
    """
    validate_credentials()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    return client
