"""
Модуль для парсинга и анализа логов аналитики Channel2PDF.

Предоставляет общую логику разбора событий из server.log,
которую можно использовать как в CLI-скриптах, так и в веб-эндпоинтах.
"""

import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class AnalyticsData:
    """
    Класс для хранения и обработки аналитических данных из логов.
    """

    def __init__(self):
        # Счётчики по типам событий
        self.events_count: Dict[str, int] = defaultdict(int)

        # Распределение по языкам
        self.lang_distribution: Dict[str, int] = defaultdict(int)

        # Ошибки по типам
        self.errors_by_type: Counter = Counter()

        # Статистика по дням: {дата: {started: N, success: N, failed: N}}
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"started": 0, "success": 0, "failed": 0}
        )

        # Топ каналов по количеству экспортов
        self.top_channels: Counter = Counter()

        # Всего обработано строк
        self.total_lines = 0
        self.valid_events = 0

    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Добавляет событие в аналитику.

        Args:
            event: Словарь с данными события из JSON
        """
        event_type = event.get("event_type")
        if not event_type:
            return

        # Счётчики событий
        self.events_count[event_type] += 1
        self.valid_events += 1

        # Распределение по языкам
        lang = event.get("lang", "unknown")
        self.lang_distribution[lang] += 1

        # Обработка экспортов для статистики по дням
        timestamp = event.get("timestamp", "")
        if timestamp and event_type in ["export_started", "export_success", "export_failed"]:
            try:
                # Парсим дату из ISO формата: "2025-11-19T12:34:56.789Z"
                date_str = timestamp.split("T")[0]  # Берём только дату

                if event_type == "export_started":
                    self.daily_stats[date_str]["started"] += 1
                elif event_type == "export_success":
                    self.daily_stats[date_str]["success"] += 1
                elif event_type == "export_failed":
                    self.daily_stats[date_str]["failed"] += 1
            except (IndexError, ValueError):
                pass  # Если дата некорректная, пропускаем

        # Обработка ошибок
        if event_type == "export_failed":
            extra = event.get("extra", {})
            error_type = extra.get("error_type", "UnknownError")
            self.errors_by_type[error_type] += 1

        # Топ каналов
        if event_type == "export_started":
            extra = event.get("extra", {})
            channel = extra.get("channel_input")
            if channel:
                self.top_channels[channel] += 1

    def get_conversion_rate(self) -> Optional[float]:
        """
        Вычисляет конверсию от started до success.

        Returns:
            float: Конверсия в процентах (0-100) или None, если нет данных
        """
        started = self.events_count.get("export_started", 0)
        success = self.events_count.get("export_success", 0)

        if started > 0:
            return (success / started) * 100
        return None

    def get_daily_stats_sorted(self, reverse: bool = True) -> List[tuple]:
        """
        Возвращает статистику по дням, отсортированную по дате.

        Args:
            reverse: Если True, сначала новые даты (по умолчанию)

        Returns:
            List[tuple]: Список кортежей (дата, stats_dict)
        """
        return sorted(
            self.daily_stats.items(),
            key=lambda x: x[0],
            reverse=reverse
        )


def parse_log_file(log_path: str = "server.log") -> AnalyticsData:
    """
    Парсит файл логов и возвращает агрегированные данные аналитики.

    Args:
        log_path: Путь к файлу логов (по умолчанию "server.log")

    Returns:
        AnalyticsData: Объект с агрегированными данными
    """
    analytics = AnalyticsData()
    log_file = Path(log_path)

    # Проверяем существование файла
    if not log_file.exists():
        return analytics

    # Читаем файл построчно
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            analytics.total_lines += 1
            line = line.strip()

            if not line:
                continue

            # Пытаемся распарсить JSON
            try:
                event = json.loads(line)

                # Проверяем, что это событие аналитики (есть event_type)
                if "event_type" in event:
                    analytics.add_event(event)
            except json.JSONDecodeError:
                # Строка не является JSON — пропускаем
                continue

    return analytics


def format_analytics_report(analytics: AnalyticsData, max_channels: int = 10) -> str:
    """
    Форматирует аналитические данные в человекочитаемый текстовый отчёт.

    Args:
        analytics: Объект с аналитическими данными
        max_channels: Максимальное количество каналов в топе

    Returns:
        str: Форматированный текстовый отчёт
    """
    lines = []
    lines.append("=" * 70)
    lines.append("АНАЛИТИКА CHANNEL2PDF")
    lines.append("=" * 70)
    lines.append("")

    # Общая информация
    lines.append(f"Всего строк в логе: {analytics.total_lines}")
    lines.append(f"Валидных событий аналитики: {analytics.valid_events}")
    lines.append("")

    # Сводка по событиям
    lines.append("-" * 70)
    lines.append("СВОДКА ПО СОБЫТИЯМ")
    lines.append("-" * 70)

    started = analytics.events_count.get("export_started", 0)
    success = analytics.events_count.get("export_success", 0)
    failed = analytics.events_count.get("export_failed", 0)

    lines.append(f"export_started:  {started:>6}")
    lines.append(f"export_success:  {success:>6}")
    lines.append(f"export_failed:   {failed:>6}")
    lines.append("")

    # Конверсия
    conversion = analytics.get_conversion_rate()
    if conversion is not None:
        lines.append(f"Конверсия (success/started): {conversion:.2f}%")
    else:
        lines.append("Конверсия: нет данных")
    lines.append("")

    # Другие события
    other_events = {k: v for k, v in analytics.events_count.items()
                    if k not in ["export_started", "export_success", "export_failed"]}
    if other_events:
        lines.append("Другие события:")
        for event_type, count in sorted(other_events.items()):
            lines.append(f"  {event_type}: {count}")
        lines.append("")

    # Распределение по языкам
    lines.append("-" * 70)
    lines.append("РАСПРЕДЕЛЕНИЕ ПО ЯЗЫКАМ")
    lines.append("-" * 70)

    if analytics.lang_distribution:
        for lang, count in sorted(analytics.lang_distribution.items(),
                                   key=lambda x: x[1], reverse=True):
            lines.append(f"{lang:>10}: {count:>6} событий")
    else:
        lines.append("Нет данных")
    lines.append("")

    # Ошибки по типам
    lines.append("-" * 70)
    lines.append("ОШИБКИ ПО ТИПАМ")
    lines.append("-" * 70)

    if analytics.errors_by_type:
        for error_type, count in analytics.errors_by_type.most_common():
            lines.append(f"{error_type:<40} — {count}")
    else:
        lines.append("Ошибок пока не было")
    lines.append("")

    # Статистика по дням
    lines.append("-" * 70)
    lines.append("СТАТИСТИКА ПО ДНЯМ")
    lines.append("-" * 70)

    daily_stats = analytics.get_daily_stats_sorted(reverse=True)
    if daily_stats:
        for date_str, stats in daily_stats:
            lines.append(
                f"{date_str}: started={stats['started']}, "
                f"success={stats['success']}, failed={stats['failed']}"
            )
    else:
        lines.append("Нет данных по дням")
    lines.append("")

    # Топ каналов
    lines.append("-" * 70)
    lines.append(f"ТОП-{max_channels} КАНАЛОВ ПО ЭКСПОРТАМ")
    lines.append("-" * 70)

    if analytics.top_channels:
        for channel, count in analytics.top_channels.most_common(max_channels):
            lines.append(f"{channel:<40} — {count} экспортов")
    else:
        lines.append("Нет данных о каналах")
    lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


if __name__ == "__main__":
    """
    Пример использования модуля для быстрого тестирования.
    """
    print("Тестирование модуля log_parser.py...")
    print()

    analytics = parse_log_file("server.log")
    report = format_analytics_report(analytics)
    print(report)
