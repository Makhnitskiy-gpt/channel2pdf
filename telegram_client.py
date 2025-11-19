"""
Модуль для работы с Telegram клиентом.
"""

from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION_NAME, TELEGRAM_SESSION_STRING, IS_PRODUCTION


def validate_credentials():
    """Проверяет, что API_ID и API_HASH заполнены."""
    if API_ID is None or API_HASH is None or API_ID == 0 or API_HASH == "":
        raise ValueError(
            "Ошибка: API_ID и API_HASH не заполнены.\n"
            "Откройте файл config.py и заполните эти значения.\n"
            "Получить их можно на https://my.telegram.org/apps"
        )


async def get_client():
    """
    Создаёт и возвращает подключённый Telegram клиент.

    В продакшене (ENV=production):
    - Использует StringSession из переменной окружения TELEGRAM_SESSION_STRING
    - НЕ делает интерактивный ввод (phone/code)
    - Требует готовую сессию

    В разработке (ENV=development):
    - Использует файловую сессию (session.session)
    - Может делать интерактивный ввод при первом запуске

    Returns:
        TelegramClient: Подключённый клиент

    Raises:
        ValueError: Если API_ID или API_HASH не заполнены
        RuntimeError: Если в продакшене не задана TELEGRAM_SESSION_STRING
    """
    validate_credentials()

    if IS_PRODUCTION:
        # Продакшен: только StringSession, без интерактивного ввода
        if not TELEGRAM_SESSION_STRING:
            raise RuntimeError(
                "TELEGRAM_SESSION_STRING не задана в переменных окружения.\n"
                "Для продакшена требуется готовая сессия.\n"
                "Сгенерируйте её локально с помощью: python generate_session.py"
            )

        # Создаём клиент с StringSession
        client = TelegramClient(
            StringSession(TELEGRAM_SESSION_STRING),
            API_ID,
            API_HASH
        )

        # Подключаемся БЕЗ интерактивного ввода
        # Если сессия невалидна - выбросит исключение
        await client.connect()

        if not await client.is_user_authorized():
            raise RuntimeError(
                "Сессия невалидна или истекла.\n"
                "Сгенерируйте новую сессию локально: python generate_session.py"
            )

        return client

    else:
        # Разработка: используем файловую сессию, разрешён интерактивный ввод
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

        # start() может запросить телефон/код при первом запуске
        await client.start()

        return client
