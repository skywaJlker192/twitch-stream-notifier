#!/usr/bin/env python3
"""
Twitch Stream Notifier — автономная версия (без API).
Где валидация: validate_channel()
Где логирование: logger
Где проверка прав: не требуется (офлайн-режим)
"""

import os
import re
import json
import time
import random
import logging
import threading
from pathlib import Path
from datetime import datetime

# --- Логирование (п.2) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notifier.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Настройки (п.5) ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"channels": ["zoinkgd"], "poll_interval": 30, "client_id": "", "demo_mode": True}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = DEFAULT_SETTINGS.copy()
                settings.update(json.load(f))
                return settings
        except Exception as e:
            logger.error(f"Ошибка чтения настроек: {e}")
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка записи настроек: {e}")

# --- Валидация (п.1: белая валидация) ---
def validate_channel(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))

# --- Уведомления ---
def show_notification(title: str, message: str):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name='Twitch Notifier', timeout=10)
    except ImportError:
        logger.warning("plyer не установлен — уведомление в консоль")
        print(f"[🔔] {title}: {message}")

# --- Мини-окно превью (заглушка) ---
def show_preview_window(channel: str):
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title(f"🔴 {channel} — LIVE")
        root.geometry("400x300")
        root.configure(bg="#1a1a1a")

        tk.Label(root, text=f"🎮 {channel}", fg="white", bg="#1a1a1a", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(root, text="Стрим запущен!", fg="#00ff00", bg="#1a1a1a").pack()
        tk.Label(root, text="(Превью появится после подключения к API)", fg="#888", bg="#1a1a1a", font=("Arial", 8)).pack(pady=20)

        frame = tk.Frame(root, bg="#000", width=320, height=180)
        frame.pack()
        frame.pack_propagate(False)
        tk.Label(frame, text="Twitch Embed\n(ожидание Client ID)", fg="#555", bg="#000").place(relx=0.5, rely=0.5, anchor="center")

        tk.Button(root, text="Открыть в браузере", command=lambda: os.startfile(f"https://twitch.tv/{channel}") if os.name=='nt' else os.system(f"open https://twitch.tv/{channel}")).pack(pady=10)

        root.after(30000, root.destroy)  # Автозакрытие через 30 сек
        root.mainloop()
    except Exception as e:
        logger.error(f"Ошибка окна превью: {e}")

# --- Демо-режим: имитация стрима ---
def demo_check(channel: str, known: set):
    # Имитация: 30% шанс "обнаружить" стрим каждые 2 цикла
    if random.random() < 0.3 and channel not in known:
        logger.info(f"[DEMO] Обнаружен стрим: {channel}")
        show_notification(f"🔴 {channel} начал стрим! (ДЕМО)", "Это тестовое уведомление")
        show_preview_window(channel)
        known.add(channel)
        # Сброс через 5 минут, чтобы можно было протестировать снова
        threading.Timer(300, lambda: known.discard(channel)).start()

# --- Реальный режим (закомментирован, раскомментируйте когда будет Client ID) ---
"""
def real_check(client_id: str, channel: str, known: set):
    import requests
    headers = {'Client-ID': client_id}
    try:
        resp = requests.get("https://api.twitch.tv/helix/streams", headers=headers, params={'user_login': channel}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for stream in data.get('data', []):
            if stream['id'] not in known:
                logger.info(f"Реальный стрим: {channel} — {stream['title']}")
                show_notification(f"🔴 {channel} начал стрим!", stream['title'])
                show_preview_window(channel)
                known.add(stream['id'])
    except Exception as e:
        logger.error(f"Ошибка API: {type(e).__name__}")
"""

# --- Основной цикл ---
def monitor_loop(settings: dict):
    channels = [ch for ch in settings['channels'] if validate_channel(ch)]
    if not channels:
        logger.error("Нет валидных каналов")
        return

    known = set()
    logger.info(f"✅ Запущено (режим: {'ДЕМО' if settings['demo_mode'] else 'REAL'}), каналы: {channels}")

    while True:
        for ch in channels:
            if settings['demo_mode']:
                demo_check(ch, known)
            else:
                # real_check(settings['client_id'], ch, known)  # ← Раскомментируйте эту строку + импорты выше
                logger.warning("REAL-режим отключен: раскомментируйте real_check() в коде")
        time.sleep(settings['poll_interval'])

# --- GUI настроек ---
def run_gui():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        logger.error("tkinter не установлен. Запуск в консольном режиме.")
        settings = load_settings()
        monitor_loop(settings)
        return

    settings = load_settings()
    root = tk.Tk()
    root.title("🎮 Twitch Notifier — Настройки")
    root.geometry("450x400")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="🔑 TWITCH_CLIENT_ID:").grid(row=0, column=0, sticky="w", pady=(0,5))
    client_id_var = tk.StringVar(value=settings.get('client_id', ''))
    ttk.Entry(frame, textvariable=client_id_var, width=40).grid(row=1, column=0, columnspan=2, pady=(0,10))

    ttk.Label(frame, text="📺 Каналы (по одному в строке):").grid(row=2, column=0, sticky="w")
    channels_text = tk.Text(frame, width=40, height=6)
    channels_text.grid(row=3, column=0, columnspan=2, pady=5)
    for ch in settings.get('channels', []):
        channels_text.insert(tk.END, ch + "\n")

    ttk.Label(frame, text="⏱ Интервал (сек):").grid(row=4, column=0, sticky="w")
    interval_var = tk.IntVar(value=settings.get('poll_interval', 30))
    ttk.Spinbox(frame, from_=10, to=300, textvariable=interval_var, width=10).grid(row=4, column=1, sticky="w")

    demo_var = tk.BooleanVar(value=settings.get('demo_mode', True))
    ttk.Checkbutton(frame, text="🧪 Демо-режим (без API)", variable=demo_var).grid(row=5, column=0, columnspan=2, pady=10)

    def save_and_start():
        channels = [c.strip().lower() for c in channels_text.get("1.0", tk.END).splitlines() if c.strip()]
        valid = [c for c in channels if validate_channel(c)]
        if not valid:
            messagebox.showerror("Ошибка", "Нет валидных каналов (только a-zA-Z0-9_, 2-25 символов)")
            return
        settings['channels'] = valid
        settings['client_id'] = client_id_var.get().strip()
        settings['poll_interval'] = interval_var.get()
        settings['demo_mode'] = demo_var.get()
        save_settings(settings)
        root.destroy()
        threading.Thread(target=monitor_loop, args=(settings,), daemon=True).start()
        # Показываем тестовое уведомление, чтобы пользователь понял, что всё работает
        show_notification("✅ Twitch Notifier запущен!", "Отслеживание активно (режим: ДЕМО)")

    ttk.Button(frame, text="💾 Сохранить и Запустить", command=save_and_start).grid(row=6, column=0, columnspan=2, pady=10)
    ttk.Label(frame, text="Совет: введите zoinkgd для теста", foreground="#666").grid(row=7, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    logger.info("🚀 Twitch Stream Notifier (автономная версия)")
    run_gui()
