# settings_manager.py
import json
import os
from typing import List, Optional

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "channels": [],
    "twitch_client_id": "",
    "poll_interval": 30
}

def load_settings() -> dict:
    """Загрузить настройки из файла. Если файла нет — создать с дефолтными значениями."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Объединяем с дефолтными на случай новых полей
                settings = DEFAULT_SETTINGS.copy()
                settings.update(loaded)
                return settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка чтения настроек, используем стандартные: {e}")
            return DEFAULT_SETTINGS
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings: dict):
    """Сохранить настройки в файл."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Ошибка записи настроек: {e}")
        raise
