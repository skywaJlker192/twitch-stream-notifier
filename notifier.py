#!/usr/bin/env python3
"""
Twitch Stream Notifier — оповещение о старте стрима.
Где валидация: validate_channel_name (п.1)
Где логирование: logger.info/error (п.2)
Где проверка прав: нет авторизации, но проверка статуса API (п.3 — не требуется)
"""

import os
import re
import time
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- Логирование (п.2) ---
# Не выводим stack trace клиенту; логируем детали только на сервере (в данном случае — локально)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notifier.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Загрузка .env (п.5) ---
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# --- Проверка обязательных секретов (п.5) ---
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
if not CLIENT_ID:
    logger.error("❌ TWITCH_CLIENT_ID не задан в .env")
    print("Ошибка: TWITCH_CLIENT_ID не задан в .env. Скопируйте .env.example в .env и укажите Client ID.")
    exit(1)

BASE_URL = "https://api.twitch.tv/helix/streams"


# --- Валидация входных данных (п.1: белая валидация) ---
def validate_channel_name(name: str) -> bool:
    """
    Где валидация: разрешены только [a-zA-Z0-9_], длина 2–25.
    Не доверяем пользовательскому вводу.
    """
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))


# --- Уведомления (без секретов, безопасно) ---
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


# --- Основная логика (п.2: обработка ошибок без утечки) ---
def check_stream(channel: str, known_streams: set):
    headers = {
        'Client-ID': CLIENT_ID,
        'Accept': 'application/vnd.twitchtv.v5+json',
    }
    params = {'user_login': channel}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
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
        # Где обработка ошибок: не показываем клиенту детали (п.2)
        logger.error(f"Ошибка при запросе к API для {channel}: {type(e).__name__}: {e}")  # логируем, но не возвращаем пользователю
    except KeyError as e:
        logger.error(f"Ошибка структуры данных от API для {channel}: ключ {e} отсутствует")  # п.2


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Twitch Stream Notifier")
    parser.add_argument('-c', '--channels', type=str, required=True, help='Каналы через запятую')
    parser.add_argument('-i', '--interval', type=int, default=30, help='Интервал в секундах')
    parser.add_argument('--dry-run', action='store_true', help='Тестовый режим: не обращаться к API, показывать моки')

    args = parser.parse_args()

    channels_input: str = args.channels
    channels: list[str] = [ch.strip().lower() for ch in channels_input.split(',')]

    validated_channels = []
    for ch in channels:
        if validate_channel_name(ch):
            validated_channels.append(ch)
        else:
            logger.warning(f"Канал '{ch}' не прошёл валидацию — пропущен")

    if not validated_channels:
        logger.error("Нет ни одного валидного канала!")
        exit(1)

    known_streams = set()
    logger.info(f"✅ Отслеживание запущено для: {validated_channels}")

    try:
        while True:
            if args.dry_run:
                # Мок: имитируем появление стрима каждые 60 сек
                for ch in validated_channels:
                    stream_id = f"mock_{ch}_{int(time.time())}"
                    if stream_id not in known_streams:
                        logger.info(f"Мок: новый стрим у {ch} (тест)")
                        show_notification(
                            title=f"🔴 {ch} начал стрим! (МОК)",
                            message="Это тестовое уведомление — API не вызывается."
                        )
                        known_streams.add(stream_id)
            else:
                for channel in validated_channels:
                    check_stream(channel, known_streams)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем.")
        exit(0)

if __name__ == "__main__":
    main()
