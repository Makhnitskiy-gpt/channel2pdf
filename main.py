"""
Консольная утилита для парсинга Telegram-каналов и создания PDF-отчётов.
"""

import asyncio
from datetime import datetime
import sys

from core_service import (
    generate_report,
    is_demo_mode,
    ChannelNotFoundError,
    NoPostsFoundError,
    TelegramConnectionError,
    ReportGenerationError
)


def get_user_input(demo_mode=False):
    """
    Получает ввод от пользователя через CLI.

    Args:
        demo_mode (bool): Если True, пропускает ввод канала

    Returns:
        dict: Словарь с параметрами для парсинга
    """
    print("=" * 60)
    print("Парсер Telegram-каналов")
    print("=" * 60)
    print()

    # Если демо-режим, показываем предупреждение
    if demo_mode:
        print("⚠️  ДЕМО-РЕЖИМ")
        print("=" * 60)
        print("API_ID или API_HASH не заданы в config.py")
        print("Программа работает с тестовыми данными без подключения к Telegram.")
        print("Ввод канала будет пропущен.")
        print("=" * 60)
        print()
        channel = "demo_channel"
    else:
        # 1. Username или ссылка на канал
        channel = input("Введите username или ссылку на канал (например, @channelname): ").strip()
        if not channel:
            print("Ошибка: канал не может быть пустым.")
            sys.exit(1)

    # 2. Дата начала периода
    while True:
        date_from_str = input("Введите дату начала периода (YYYY-MM-DD): ").strip()
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            break
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте формат YYYY-MM-DD (например, 2024-01-15).")

    # 3. Дата конца периода
    while True:
        date_to_str = input("Введите дату конца периода (YYYY-MM-DD): ").strip()
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            if date_to < date_from:
                print("Ошибка: дата конца не может быть раньше даты начала.")
                continue
            break
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте формат YYYY-MM-DD (например, 2024-01-15).")

    # 4. Тип сортировки
    print()
    print("Выберите тип сортировки:")
    print("  1 - по дате")
    print("  2 - по количеству реакций")
    print("  3 - по количеству просмотров")

    while True:
        sort_choice = input("Введите номер (1-3): ").strip()
        if sort_choice in ['1', '2', '3']:
            break
        print("Ошибка: выберите 1, 2 или 3.")

    sort_type_map = {
        '1': 'date',
        '2': 'reactions',
        '3': 'views'
    }
    sort_type = sort_type_map[sort_choice]

    # 5. Направление сортировки
    print()
    print("Выберите направление сортировки:")
    print("  1 - по возрастанию")
    print("  2 - по убыванию")

    while True:
        direction_choice = input("Введите номер (1-2): ").strip()
        if direction_choice in ['1', '2']:
            break
        print("Ошибка: выберите 1 или 2.")

    ascending = direction_choice == '1'

    # 6. Имя PDF-файла
    print()
    default_filename = f"{channel.replace('@', '').replace('/', '_')}_{date_from}_{date_to}.pdf"
    filename = input(f"Введите имя PDF-файла (Enter для '{default_filename}'): ").strip()

    if not filename:
        filename = default_filename

    if not filename.endswith('.pdf'):
        filename += '.pdf'

    return {
        'channel': channel,
        'date_from': date_from,
        'date_to': date_to,
        'sort_type': sort_type,
        'ascending': ascending,
        'filename': filename
    }


async def main():
    """Главная функция программы."""
    try:
        # Проверяем режим работы
        demo_mode = is_demo_mode()

        # Получаем параметры от пользователя
        params = get_user_input(demo_mode=demo_mode)

        print()
        print("=" * 60)

        if demo_mode:
            print("Генерация тестовых данных...")
        else:
            print("Подключение к Telegram и получение постов...")

        print(f"Канал: {params['channel']}")
        print(f"Период: с {params['date_from']} по {params['date_to']}")
        print()

        # Генерируем отчёт через core_service
        sort_type_names = {
            'date': 'дате',
            'reactions': 'количеству реакций',
            'views': 'количеству просмотров'
        }
        direction_name = 'по возрастанию' if params['ascending'] else 'по убыванию'

        print(f"Сортировка по {sort_type_names[params['sort_type']]} ({direction_name})...")
        print(f"Создание PDF-файла: {params['filename']}...")
        print()

        pdf_path = await generate_report(
            channel=params['channel'],
            date_from=params['date_from'],
            date_to=params['date_to'],
            sort_type=params['sort_type'],
            ascending=params['ascending'],
            filename=params['filename'],
            output_dir="."  # Сохраняем в текущую директорию для CLI
        )

        print("=" * 60)
        print("Готово!")
        print(f"PDF-файл создан: {pdf_path}")
        if demo_mode:
            print()
            print("ℹ️  Это был демо-режим с тестовыми данными.")
            print("Для работы с реальными каналами заполните API_ID и API_HASH")
            print("в файле config.py и установите DEMO_MODE = False")
        print("=" * 60)

    except ChannelNotFoundError as e:
        print()
        print("=" * 60)
        print(f"Ошибка: {e}")
        print("=" * 60)
        sys.exit(1)

    except NoPostsFoundError as e:
        print()
        print("=" * 60)
        print(str(e))
        print("=" * 60)
        sys.exit(0)

    except TelegramConnectionError as e:
        print()
        print("=" * 60)
        print(f"Ошибка подключения: {e}")
        print("=" * 60)
        sys.exit(1)

    except ReportGenerationError as e:
        print()
        print("=" * 60)
        print(f"Ошибка генерации отчёта: {e}")
        print("=" * 60)
        sys.exit(1)

    except ValueError as e:
        print()
        print("=" * 60)
        print(f"Ошибка: {e}")
        print("=" * 60)
        sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("Операция отменена пользователем.")
        sys.exit(0)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"Неожиданная ошибка: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Запускаем асинхронную главную функцию
    asyncio.run(main())
