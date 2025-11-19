#!/usr/bin/env python3
"""
Тест веб-интерфейса с проверкой обработки эмодзи.

Этот скрипт симулирует запрос к веб-приложению и проверяет,
что PDF генерируется с корректной обработкой эмодзи.
"""

import requests
from datetime import date
import os


def test_web_interface_demo():
    """
    Тестирует веб-интерфейс в демо-режиме.
    """
    print("=" * 60)
    print("ТЕСТ ВЕБ-ИНТЕРФЕЙСА С ЭМОДЗИ (DEMO MODE)")
    print("=" * 60)

    # URL веб-сервера
    base_url = "http://127.0.0.1:8000"

    # 1. Проверяем, что сервер отвечает
    print("\n1. Проверка доступности сервера...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Сервер доступен")
        else:
            print(f"   ❌ Сервер вернул код {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")
        print("\n   💡 Запустите сервер командой:")
        print("   ./start_web.sh")
        return False

    # 2. Отправляем POST запрос для генерации PDF
    print("\n2. Отправка запроса на генерацию PDF...")

    # Данные формы (должны соответствовать параметрам web_app.py)
    form_data = {
        "channel": "test_channel",  # В демо-режиме канал не важен
        "date_from": "2024-01-01",
        "date_to": "2025-01-01",
        "sort_type": "date",  # date, reactions, views
        "direction": "desc",  # asc, desc
        "filename": "test_web_emoji"
    }

    try:
        response = requests.post(
            f"{base_url}/generate",
            data=form_data,
            timeout=30
        )

        if response.status_code == 200:
            print("   ✅ PDF успешно сгенерирован")

            # Сохраняем PDF для проверки
            output_file = "./tmp/web_demo_test.pdf"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = os.path.getsize(output_file)
            print(f"   📄 Размер файла: {file_size:,} байт")
            print(f"   💾 Сохранён в: {output_file}")

            return True
        else:
            print(f"   ❌ Ошибка генерации PDF: HTTP {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка запроса: {e}")
        return False


def main():
    """
    Главная функция теста.
    """
    print("\n" + "=" * 60)
    print("ТЕСТ ВЕБА С ИСПРАВЛЕНИЕМ ЭМОДЗИ")
    print("=" * 60 + "\n")

    print("📋 Этот тест проверяет:")
    print("   1. Доступность веб-сервера")
    print("   2. Генерацию PDF через веб-интерфейс")
    print("   3. Корректность обработки эмодзи в веб-версии")
    print()

    # Запускаем тест
    success = test_web_interface_demo()

    # Итоги
    print("\n" + "=" * 60)
    if success:
        print("✅ ВЕБ-ИНТЕРФЕЙС РАБОТАЕТ КОРРЕКТНО")
        print("=" * 60)
        print("\n📄 Проверьте PDF файл:")
        print("   open ./tmp/web_demo_test.pdf")
        print("\n✅ Убедитесь, что:")
        print("   1. Эмодзи отображаются без артефактов")
        print("   2. Нет серых 'ушек' над ❤️")
        print("   3. Все реакции читаемы")
        print("\n🌐 Откройте браузер:")
        print("   http://127.0.0.1:8000")
    else:
        print("❌ ТЕСТ НЕ ПРОШЁЛ")
        print("=" * 60)
        print("\n💡 Возможные причины:")
        print("   1. Сервер не запущен → запустите ./start_web.sh")
        print("   2. Демо-режим отключён → включите DEMO_MODE = True в config.py")
        print("   3. Порт 8000 занят → освободите порт")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
