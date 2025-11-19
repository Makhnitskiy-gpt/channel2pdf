"""
Модуль для получения постов из Telegram-канала.
"""

from datetime import datetime, timezone, timedelta, date
from telethon.errors import UsernameInvalidError, ChannelPrivateError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage


def get_demo_posts(date_from, date_to):
    """
    Генерирует тестовые посты для демо-режима.

    Args:
        date_from (datetime.date): Начало периода
        date_to (datetime.date): Конец периода

    Returns:
        list: Список словарей с данными тестовых постов
    """
    # Вычисляем диапазон дней
    days_range = (date_to - date_from).days
    if days_range < 0:
        days_range = 0

    # Создаём 7 тестовых постов
    demo_posts = []

    # Пост 1: С реакциями и просмотрами, короткий текст
    post_date_1 = date_from + timedelta(days=min(0, days_range))
    demo_posts.append({
        "date": post_date_1,
        "text": "Первый демо-пост! Короткий текст с реакциями и просмотрами.",
        "views": 1543,
        "reactions": [
            {"emoji": "❤️", "count": 120},
            {"emoji": "👍", "count": 85},
            {"emoji": "🔥", "count": 42}
        ]
    })

    # Пост 2: С реакциями и просмотрами, длинный текст
    post_date_2 = date_from + timedelta(days=min(1, days_range))
    demo_posts.append({
        "date": post_date_2,
        "text": """Это второй демо-пост с более длинным текстом.

Здесь несколько абзацев, чтобы продемонстрировать, как PDF-генератор обрабатывает многострочный контент.

В этом посте также есть реакции и просмотры. Это помогает протестировать форматирование шапки поста в PDF-документе.

Третий абзац добавлен для полноты картины.""",
        "views": 2847,
        "reactions": [
            {"emoji": "😂", "count": 230},
            {"emoji": "❤️", "count": 156},
            {"emoji": "🎉", "count": 94}
        ]
    })

    # Пост 3: Только просмотры, без реакций
    post_date_3 = date_from + timedelta(days=min(2, days_range))
    demo_posts.append({
        "date": post_date_3,
        "text": "Третий пост — без реакций, но с просмотрами. Проверяем, что блок реакций не отображается.",
        "views": 987,
        "reactions": []
    })

    # Пост 4: Без просмотров, но с реакциями
    post_date_4 = date_from + timedelta(days=min(3, days_range))
    demo_posts.append({
        "date": post_date_4,
        "text": "Четвёртый пост: есть реакции, но нет просмотров. Проверяем корректность отображения.",
        "views": None,
        "reactions": [
            {"emoji": "👏", "count": 67},
            {"emoji": "💯", "count": 45}
        ]
    })

    # Пост 5: Без реакций и просмотров
    post_date_5 = date_from + timedelta(days=min(4, days_range))
    demo_posts.append({
        "date": post_date_5,
        "text": "Пятый пост — минималистичный. Ни реакций, ни просмотров. Только дата и текст.",
        "views": None,
        "reactions": []
    })

    # Пост 6: Много реакций, мало просмотров
    post_date_6 = date_from + timedelta(days=min(5, days_range))
    demo_posts.append({
        "date": post_date_6,
        "text": """Шестой пост с огромным количеством реакций!

Этот пост особенно популярен по реакциям, но просмотров у него немного.

Используется для тестирования сортировки по реакциям.""",
        "views": 543,
        "reactions": [
            {"emoji": "🔥", "count": 890},
            {"emoji": "❤️", "count": 723},
            {"emoji": "😍", "count": 612}
        ]
    })

    # Пост 7: Очень длинный текст, средние показатели
    post_date_7 = date_from + timedelta(days=min(6, days_range))
    demo_posts.append({
        "date": post_date_7,
        "text": """Седьмой пост — самый длинный из всех!

Этот текст специально создан для проверки того, как PDF-генератор справляется с большими объёмами текста.

Абзац первый: здесь мы говорим о важности тестирования различных edge cases при разработке программного обеспечения.

Абзац второй: особенно важно проверять, как система обрабатывает граничные случаи — например, очень длинные тексты, отсутствие данных, или необычные комбинации параметров.

Абзац третий: в данном случае мы тестируем PDF-генератор, который должен корректно отображать длинный многострочный текст с сохранением всех переносов строк и форматирования.

Абзац четвёртый: также важно убедиться, что шапка поста (дата, реакции, просмотры) корректно отображается даже для длинных постов.

Финальный абзац: если вы видите этот текст в PDF-файле с правильным форматированием — всё работает отлично!""",
        "views": 1876,
        "reactions": [
            {"emoji": "📚", "count": 234},
            {"emoji": "👍", "count": 187},
            {"emoji": "🤔", "count": 156}
        ]
    })

    # Фильтруем посты по диапазону дат (на случай, если date_to раньше всех постов)
    filtered_posts = [
        post for post in demo_posts
        if date_from <= post['date'] <= date_to
    ]

    return filtered_posts


async def fetch_posts(channel, date_from, date_to, client):
    """
    Получает посты из канала за указанный период.

    Args:
        channel (str): Username канала (с @ или без) или ссылка
        date_from (datetime.date): Начало периода
        date_to (datetime.date): Конец периода
        client (TelegramClient): Подключённый Telegram клиент

    Returns:
        list: Список словарей с данными постов:
            {
                "date": datetime.date,
                "text": str,
                "views": int | None,
                "reactions": [{"emoji": str, "count": int}, ...]
            }

    Raises:
        ValueError: Если канал не найден или недоступен
    """
    # Очищаем username от лишних символов
    channel_username = channel.strip()
    if channel_username.startswith('@'):
        channel_username = channel_username[1:]
    if 't.me/' in channel_username:
        channel_username = channel_username.split('t.me/')[-1]

    try:
        # Получаем сущность канала
        entity = await client.get_entity(channel_username)
    except UsernameInvalidError:
        raise ValueError(f"Канал '{channel}' не найден. Проверьте правильность username.")
    except ChannelPrivateError:
        raise ValueError(f"Канал '{channel}' является приватным или недоступным.")
    except Exception as e:
        raise ValueError(f"Не удалось получить доступ к каналу '{channel}': {str(e)}")

    # Конвертируем даты в datetime для сравнения
    datetime_from = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
    datetime_to = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=timezone.utc)

    posts = []

    # Получаем сообщения из канала
    async for message in client.iter_messages(entity, offset_date=datetime_to, reverse=False):
        # Проверяем дату сообщения
        if message.date < datetime_from:
            break  # Вышли за пределы периода

        if message.date > datetime_to:
            continue  # Ещё не достигли начала периода

        # Пропускаем сообщения без текста
        if not message.text or message.text.strip() == "":
            continue

        # Получаем просмотры
        views = message.views if hasattr(message, 'views') else None

        # Получаем реакции
        reactions = []
        if hasattr(message, 'reactions') and message.reactions is not None:
            reaction_list = message.reactions.results
            # Сортируем по количеству и берём топ-3
            sorted_reactions = sorted(reaction_list, key=lambda x: x.count, reverse=True)[:3]

            for reaction in sorted_reactions:
                # Получаем emoji из реакции
                if hasattr(reaction.reaction, 'emoticon'):
                    emoji = reaction.reaction.emoticon
                else:
                    # Для кастомных эмодзи используем заглушку
                    emoji = "👍"

                reactions.append({
                    "emoji": emoji,
                    "count": reaction.count
                })

        posts.append({
            "date": message.date.date(),
            "text": message.text,
            "views": views,
            "reactions": reactions
        })

    return posts


def sort_posts(posts, sort_type, ascending=True):
    """
    Сортирует посты по заданному критерию.

    Args:
        posts (list): Список постов
        sort_type (str): Тип сортировки: 'date', 'reactions', 'views'
        ascending (bool): True для возрастания, False для убывания

    Returns:
        list: Отсортированный список постов
    """
    if sort_type == 'date':
        return sorted(posts, key=lambda x: x['date'], reverse=not ascending)

    elif sort_type == 'reactions':
        def get_reactions_sum(post):
            return sum(r['count'] for r in post['reactions'])

        return sorted(posts, key=get_reactions_sum, reverse=not ascending)

    elif sort_type == 'views':
        def get_views(post):
            return post['views'] if post['views'] is not None else 0

        return sorted(posts, key=get_views, reverse=not ascending)

    else:
        raise ValueError(f"Неизвестный тип сортировки: {sort_type}")
