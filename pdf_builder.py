"""
Модуль для создания PDF-файлов с постами.
"""

from weasyprint import HTML, CSS
import os
import re
from html import escape
from emoji_handler import (
    normalize_emoji_text,
    format_reactions_list,
    get_emoji_font_css,
    get_emoji_safe_font_family
)


def clean_markdown(text):
    """
    Удаляет markdown-разметку из текста.

    Args:
        text (str): Исходный текст с markdown

    Returns:
        str: Текст без markdown-разметки
    """
    # Удаляем жирный текст (**text** или __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)

    # Удаляем курсив (*text* или _text_)
    text = re.sub(r'\*([^\*]+?)\*', r'\1', text)
    text = re.sub(r'_([^_]+?)_', r'\1', text)

    # Удаляем зачёркнутый текст (~~text~~)
    text = re.sub(r'~~(.+?)~~', r'\1', text, flags=re.DOTALL)

    # Удаляем моноширинный текст (`text` или ```text```)
    text = re.sub(r'```(.+?)```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.+?)`', r'\1', text)

    # Удаляем ссылки [text](url), оставляя только text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # Удаляем одиночные звёздочки и подчёркивания в начале и конце строк
    text = re.sub(r'^\*+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*\*+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^_+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*_+$', '', text, flags=re.MULTILINE)

    # Удаляем символы маркированных списков
    text = re.sub(r'^\s*[-\*\+]\s+', '', text, flags=re.MULTILINE)

    return text


def create_html(posts, channel_name):
    """
    Создаёт HTML-разметку для PDF.

    Args:
        posts (list): Список постов
        channel_name (str): Название канала

    Returns:
        str: HTML-код
    """
    # CSS-стили для красивого оформления
    # Включаем явное подключение emoji-шрифтов
    emoji_fonts_css = get_emoji_font_css()

    css = f"""
    {emoji_fonts_css}

    @page {{
        size: A4;
        margin: 2cm;
    }}

    body {{
        font-family: {get_emoji_safe_font_family()};
        font-size: 12pt;
        line-height: 1.6;
        color: #333;
    }}

    h1 {{
        font-size: 18pt;
        font-weight: 600;
        color: #000;
        margin-bottom: 1.5em;
        padding-bottom: 0.5em;
        border-bottom: 2px solid #e0e0e0;
    }}

    .post {{
        margin-bottom: 2em;
        page-break-inside: avoid;
    }}

    .post-header {{
        font-size: 11pt;
        color: #666;
        margin-bottom: 0.5em;
        font-weight: 500;
    }}

    .post-date {{
        color: #0066cc;
        font-weight: 600;
    }}

    .post-reactions {{
        color: #555;
    }}

    .post-views {{
        color: #555;
    }}

    .post-text {{
        font-size: 12pt;
        line-height: 1.6;
        color: #333;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}

    .separator {{
        border-bottom: 1px solid #e0e0e0;
        margin: 1.5em 0;
    }}
    """

    # Начало HTML-документа
    # Нормализуем эмодзи в названии канала
    normalized_channel_name = normalize_emoji_text(channel_name)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {css}
        </style>
    </head>
    <body>
        <h1>Посты из канала {escape(normalized_channel_name)}</h1>
    """

    # Добавляем каждый пост
    for i, post in enumerate(posts):
        # Формируем шапку поста
        header_parts = []

        # Дата
        date_str = post['date'].strftime('%d.%m.%Y')
        header_parts.append(f'<span class="post-date">[{date_str}]</span>')

        # Реакции - используем специальную обработку эмодзи
        if post['reactions']:
            # Форматируем реакции с нормализацией эмодзи и неразрывными пробелами
            reactions_str = format_reactions_list(post['reactions'])
            header_parts.append(f'<span class="post-reactions">{reactions_str}</span>')

        # Просмотры
        if post['views'] is not None:
            header_parts.append(f'<span class="post-views">Просмотры: {post["views"]}</span>')

        header_html = " / ".join(header_parts)

        # Текст поста (очищаем от markdown, нормализуем эмодзи и экранируем HTML)
        post_text = clean_markdown(post['text'])
        # Нормализуем эмодзи в тексте поста для корректного отображения
        post_text = normalize_emoji_text(post_text)
        post_text = escape(post_text)

        # Добавляем пост
        html += f"""
        <div class="post">
            <div class="post-header">{header_html}</div>
            <div class="post-text">{post_text}</div>
        </div>
        """

        # Разделитель между постами (кроме последнего)
        if i < len(posts) - 1:
            html += '<div class="separator"></div>'

    # Закрываем HTML-документ
    html += """
    </body>
    </html>
    """

    return html


def create_pdf(posts, filename, channel_name):
    """
    Создаёт PDF-файл с постами.

    Args:
        posts (list): Список постов для включения в PDF
        filename (str): Имя файла для сохранения
        channel_name (str): Название канала для заголовка

    Returns:
        str: Путь к созданному файлу
    """
    # Создаём HTML
    html_content = create_html(posts, channel_name)

    # Конвертируем HTML в PDF
    HTML(string=html_content).write_pdf(filename)

    return os.path.abspath(filename)
