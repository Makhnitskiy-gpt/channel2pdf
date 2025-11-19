#!/usr/bin/env python3
"""
Скрипт для генерации строковой сессии Telegram.

Этот скрипт нужно запустить ОДИН РАЗ локально, чтобы получить
строку сессии (TELEGRAM_SESSION_STRING) для использования в продакшене.

Использование:
    python generate_session.py

После успешной авторизации скрипт выведет строку сессии,
которую нужно добавить в переменные окружения на Render.
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH


async def main():
    print("=" * 60)
    print("Генерация строковой сессии для Telegram")
    print("=" * 60)
    print()
    print("Этот скрипт создаст строковую сессию для использования")
    print("в продакшене (Render.com) без интерактивного ввода.")
    print()
    print("Вам потребуется:")
    print("  1. Номер телефона, привязанный к Telegram")
    print("  2. Код подтверждения из Telegram")
    print("  3. Пароль двухфакторной аутентификации (если включен)")
    print()
    print("=" * 60)
    print()

    # Проверяем API credentials
    if not API_ID or not API_HASH or API_ID == 0 or API_HASH == "":
        print("❌ ОШИБКА: API_ID и API_HASH не заданы!")
        print()
        print("Откройте config.py и установите значения:")
        print("  API_ID = ваш_api_id")
        print("  API_HASH = 'ваш_api_hash'")
        print()
        print("Получить их можно на: https://my.telegram.org/apps")
        return

    print(f"✅ API_ID: {API_ID}")
    print(f"✅ API_HASH: {API_HASH[:10]}...")
    print()

    # Создаём клиент с пустой StringSession
    client = TelegramClient(StringSession(), API_ID, API_HASH)

    print("🔄 Подключаемся к Telegram...")
    await client.start()

    print()
    print("=" * 60)
    print("✅ УСПЕШНО! Авторизация завершена.")
    print("=" * 60)
    print()

    # Получаем строку сессии
    session_string = client.session.save()

    print("📋 Ваша строковая сессия:")
    print()
    print("-" * 60)
    print(session_string)
    print("-" * 60)
    print()

    print("📝 Что делать дальше:")
    print()
    print("1. Скопируйте строку выше (всю целиком)")
    print()
    print("2. Откройте Render Dashboard:")
    print("   https://dashboard.render.com")
    print()
    print("3. Найдите ваш сервис 'channel2pdf'")
    print()
    print("4. Перейдите в Environment → Add Environment Variable")
    print()
    print("5. Добавьте переменную:")
    print("   Key:   TELEGRAM_SESSION_STRING")
    print("   Value: [вставьте скопированную строку]")
    print()
    print("6. Сохраните изменения")
    print()
    print("7. Render автоматически перезапустит сервис")
    print()
    print("=" * 60)
    print("⚠️  ВАЖНО: Храните эту строку в секрете!")
    print("   С её помощью можно получить доступ к вашему Telegram.")
    print("=" * 60)
    print()

    # Отключаемся
    await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ ОШИБКА: {e}")
        print("\nПроверьте:")
        print("  - API_ID и API_HASH корректны")
        print("  - Интернет-соединение активно")
        print("  - Номер телефона введён в международном формате (+7...)")
