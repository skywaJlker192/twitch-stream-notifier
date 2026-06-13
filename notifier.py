#!/usr/bin/env python3
"""
Twitch Stream Notifier — автономная версия (без API).
Где валидация: validate_channel() (п.1)
Где логирование: logger (п.2)
Где проверка прав: не требуется (офлайн-режим) (п.3)
"""

import os
import re
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime

# --- Логирование (п.2: без PII, детали только в файл) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notifier.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Настройки (п.5: секреты из env/файла, не хардкод) ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "channels": ["zoinkgd"],
    "poll_interval": 30,
    "client_id": os.getenv("TWITCH_CLIENT_ID", ""),  # п.5: приоритет переменной окружения
    "demo_mode": True
}

def load_settings():
    """Загрузка настроек с проверкой (п.5, п.10)"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = DEFAULT_SETTINGS.copy()
                settings.update(json.load(f))
                return settings
        except Exception as e:
            logger.error(f"Ошибка чтения настроек: {e}")  # п.2: логирование без утечки
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

def save_settings(settings):
    """Сохранение настроек (п.5: без логирования секретов)"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            # Не логируем client_id при записи
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка записи настроек: {e}")  # п.2

# --- Валидация (п.1: белая валидация) ---
# Где валидация: разрешены только [a-zA-Z0-9_], длина 2-25
def validate_channel(name: str) -> bool:
    """Белая валидация имени канала (п.1)"""
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))

# --- Уведомления ---
# Где обработка ошибок: try/except без утечки stack trace (п.2)
def show_notification(title: str, message: str):
    """Системное уведомление (без логирования персональных данных)"""
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name='Twitch Notifier', timeout=10)
    except ImportError:
        logger.warning("plyer не установлен — уведомление в консоль")  # п.2
        print(f"[🔔] {title}: {message}")  # Общие сообщения клиенту (п.2)

# --- Мини-окно превью (заглушка) ---
# Где обработка ошибок: try/except (п.2)
def show_preview_window(channel: str):
    """Окно превью стрима (п.4: нет конкатенации пользовательского ввода в команды)"""
    try:
        import tkinter as tk
        # Валидация канала перед использованием (п.1)
        if not validate_channel(channel):
            logger.warning(f"Невалидный канал в превью: {channel}")
            return

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

        # Безопасное открытие ссылки (п.4: нет конкатенации в команду оболочки)
        def open_browser():
            import webbrowser
            url = f"https://twitch.tv/{channel}"
            # Валидация: channel уже проверен в validate_channel()
            webbrowser.open(url)

        tk.Button(root, text="Открыть в браузере", command=open_browser).pack(pady=10)

        root.after(30000, root.destroy)  # Автозакрытие через 30 сек
        root.mainloop()
    except Exception as e:
        logger.error(f"Ошибка окна превью: {type(e).__name__}")  # п.2: только тип ошибки, не stack trace

# --- Демо-режим: показываем ВСЕ стримеры сразу (ИСПРАВЛЕНО) ---
# Где валидация: канал уже проверен в monitor_loop() (п.1)
def demo_check(channel: str, known: set):
    """Демо-проверка: показывает стримера гарантированно (без случайности)"""
    if channel not in known:
        logger.info(f"[DEMO] Обнаружен стрим: {channel}")  # п.2: логирование
        show_notification(f"🔴 {channel} начал стрим! (ДЕМО)", "Это тестовое уведомление")
        show_preview_window(channel)
        known.add(channel)
        # Сброс через 5 минут для повторного теста (п.6: защита от спам-уведомлений)
        threading.Timer(300, lambda c=channel: known.discard(c)).start()

# --- Реальный режим (закомментирован, раскомментируйте когда будет Client ID) ---
"""
# Где валидация: client_id из настроек, канал проверен (п.1, п.5)
# Где обработка ошибок: try/except без утечки (п.2)
def real_check(client_id: str, channel: str, known: set):
    import requests
    headers = {'Client-ID': client_id}  # п.5: client_id из настроек
    try:
        resp = requests.get("https://api.twitch.tv/helix/streams",
                          headers=headers,
                          params={'user_login': channel},  # п.1: channel валидирован
                          timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for stream in data.get('data', []):
            if stream['id'] not in known:
                logger.info(f"Реальный стрим: {channel} — {stream['title']}")  # п.2
                show_notification(f"🔴 {channel} начал стрим!", stream['title'])
                show_preview_window(channel)
                known.add(stream['id'])
    except requests.RequestException as e:
        logger.error(f"Ошибка API: {type(e).__name__}")  # п.2: без деталей
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {type(e).__name__}")  # п.2
"""

# --- Основной цикл (ИСПРАВЛЕНО: показывает всех стримеров сразу) ---
# Где валидация: filter(validate_channel) (п.1)
# Где обработка ошибок: try/except KeyboardInterrupt (п.2)
def monitor_loop(settings: dict):
    """Основной цикл мониторинга (п.6: rate limiting через time.sleep)"""
    # п.1: белая валидация каналов
    channels = [ch for ch in settings['channels'] if validate_channel(ch)]
    if not channels:
        logger.error("Нет валидных каналов")  # п.2
        return

    known = set()
    mode_str = 'ДЕМО' if settings['demo_mode'] else 'REAL'
    logger.info(f"✅ Запущено (режим: {mode_str}), каналы: {channels}")

    # ИСПРАВЛЕНО: первый запуск — показываем ВСЕХ стримеров сразу
    if settings['demo_mode'] and not known:
        logger.info("🎬 Демо-режим: показываем всех стримеров из списка...")
        for i, ch in enumerate(channels):
            demo_check(ch, known)
            # Небольшая задержка между окнами, чтобы не накладывались (п.6)
            time.sleep(1.5)

    try:
        while True:
            for ch in channels:
                if settings['demo_mode']:
                    # В демо-режиме после первого показа просто ждём следующего цикла
                    pass
                else:
                    # real_check(settings['client_id'], ch, known)  # п.5: client_id из настроек
                    logger.warning("REAL-режим отключен: раскомментируйте real_check() в коде")
            # п.6: rate limiting — пауза между циклами опроса
            time.sleep(settings['poll_interval'])
    except KeyboardInterrupt:
        logger.info("⏹ Мониторинг остановлен пользователем")  # п.2
        # Корректное завершение: daemon-потоки завершатся автоматически
        import sys
        sys.exit(0)

# --- GUI настроек ---
# Где валидация: перед сохранением (п.1)
# Где обработка ошибок: messagebox для пользователя, logger для деталей (п.2)
def run_gui():
    """GUI для настройки (п.9: комментарии в коде)"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        logger.error("tkinter не установлен. Запуск в консольном режиме.")  # п.2
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

    # п.5: поле для Client ID (берётся из env/файла, не хардкодится)
    ttk.Label(frame, text="🔑 TWITCH_CLIENT_ID:").grid(row=0, column=0, sticky="w", pady=(0,5))
    client_id_var = tk.StringVar(value=settings.get('client_id', ''))
    ttk.Entry(frame, textvariable=client_id_var, width=40).grid(row=1, column=0, columnspan=2, pady=(0,10))

    # п.1: поле для каналов (валидация при сохранении)
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
        """Сохранение и запуск (п.1: валидация, п.5: сохранение секретов)"""
        # п.1: белая валидация каналов
        raw_channels = channels_text.get("1.0", tk.END).splitlines()
        channels = [c.strip().lower() for c in raw_channels if c.strip()]
        valid = [c for c in channels if validate_channel(c)]

        if not valid:
            # п.2: общее сообщение клиенту, детали в лог
            messagebox.showerror("Ошибка", "Нет валидных каналов (только a-zA-Z0-9_, 2-25 символов)")
            logger.warning(f"Попытка сохранить невалидные каналы: {channels}")
            return

        # п.5: сохранение настроек (без логирования client_id)
        settings['channels'] = valid
        settings['client_id'] = client_id_var.get().strip()
        settings['poll_interval'] = interval_var.get()
        settings['demo_mode'] = demo_var.get()
        save_settings(settings)

        root.destroy()

        # Запуск мониторинга в отдельном потоке
        threading.Thread(target=monitor_loop, args=(settings,), daemon=True).start()

        # п.2: уведомление пользователю без технических деталей
        show_notification("✅ Twitch Notifier запущен!", "Отслеживание активно (режим: ДЕМО)")

    ttk.Button(frame, text="💾 Сохранить и Запустить", command=save_and_start).grid(row=6, column=0, columnspan=2, pady=10)
    ttk.Label(frame, text="Совет: введите zoinkgd для теста", foreground="#666").grid(row=7, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    logger.info("🚀 Twitch Stream Notifier (автономная версия)")
    # п.2: обработка прерывания без утечки stack trace
    try:
        run_gui()
    except KeyboardInterrupt:
        logger.info("👋 Программа остановлена пользователем")
        import sys
        sys.exit(0)
