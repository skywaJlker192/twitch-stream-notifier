# notifier_core.py
# Содержит ту же логику, что и раньше, но как функция, принимающая настройки

import time
import requests
import logging
from datetime import datetime
from pathlib import Path
import os

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notifier.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Валидация ---
def validate_channel_name(name: str) -> bool:
    import re
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))

# --- Уведомления ---
def show_notification(title: str, message: str):
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name='Twitch Notifier',
            timeout=10
        )
    except ImportError:
        logger.warning("plyer не установлен — уведомление через консоль")
        print(f"[УВЕДОМЛЕНИЕ] {title}: {message}")

# --- Основная логика ---
def check_stream(client_id: str, channel: str, known_streams: set):
    headers = {
        'Client-ID': client_id,
        'Accept': 'application/vnd.twitchtv.v5+json',
    }
    params = {'user_login': channel}

    try:
        response = requests.get("https://api.twitch.tv/helix/streams", headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        streams = data.get('data', [])
        for stream in streams:
            stream_id = stream['id']
            if stream_id not in known_streams:
                logger.info(f"Новый стрим у {channel}: {stream['title']}")
                show_notification(
                    title=f"🔴 {channel} начал стрим!",
                    message=stream['title']
                )
                known_streams.add(stream_id)

    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к API для {channel}: {type(e).__name__}: {e}")
    except KeyError as e:
        logger.error(f"Ошибка структуры данных от API для {channel}: ключ {e} отсутствует")


def run_monitoring(channels: list, interval: int, client_id: str):
    """Основной цикл отслеживания, вызывается из GUI."""
    if not client_id:
        logger.error("❌ TWITCH_CLIENT_ID не задан, невозможно запустить отслеживание.")
        print("Ошибка: TWITCH_CLIENT_ID не задан.")
        return

    # Валидация каналов из GUI
    validated_channels = []
    for ch in channels:
        if validate_channel_name(ch):
            validated_channels.append(ch)
        else:
            logger.warning(f"Канал '{ch}' не прошёл валидацию — пропущен (п.1)")

    if not validated_channels:
        logger.error("Нет ни одного валидного канала! (п.1)")
        print("Нет валидных каналов для отслеживания.")
        return

    known_streams = set()
    logger.info(f"✅ Отслеживание запущено для: {validated_channels}")

    try:
        while True:
            for channel in validated_channels:
                check_stream(client_id, channel, known_streams)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем.")
        print("Отслеживание остановлено.")
