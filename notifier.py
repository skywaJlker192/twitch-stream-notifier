#!/usr/bin/env python3
"""
Twitch Stream Notifier — Production Edition
Где валидация: validate_channel() (п.1)
Где логирование: logger (п.2)
Где проверка прав: Client ID + OAuth токен из .env (п.5)
"""

from dotenv import load_dotenv
load_dotenv()

import os, re, json, time, logging, threading, webbrowser
from pathlib import Path

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
DEFAULT_SETTINGS = {
    "poll_interval": 30,
    "client_id": os.getenv("TWITCH_CLIENT_ID", ""),
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                s = DEFAULT_SETTINGS.copy()
                s.update(json.load(f))
                return s
        except Exception as e:
            logger.error(f"Ошибка чтения: {e}")
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

def save_settings(s):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка записи: {e}")

# --- Валидация (п.1) ---
def validate_channel(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))

# --- Уведомления ---
def show_notification(title: str, message: str):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name='Twitch Notifier', timeout=10)
    except:
        logger.warning("plyer не установлен")
        print(f"[🔔] {title}: {message}")

# --- Окно превью ---
def show_preview_window(channel: str):
    """Открывает стрим в браузере"""
    try:
        import tkinter as tk

        if not validate_channel(channel):
            return

        root = tk.Tk()
        root.title(f"🔴 {channel} — LIVE")
        root.geometry("400x250")
        root.configure(bg="#1a1a1a")
        root.attributes("-topmost", True)

        tk.Label(root, text=f"🎮 {channel}", fg="#9146FF", bg="#1a1a1a",
                font=("Segoe UI", 18, "bold")).pack(pady=15)
        tk.Label(root, text="✅ Стрим запущен!", fg="#00ff00", bg="#1a1a1a",
                font=("Segoe UI", 12)).pack(pady=5)
        tk.Label(root, text="Открываю стрим в браузере...",
                fg="#888", bg="#1a1a1a").pack(pady=10)

        def open_stream():
            url = f"https://twitch.tv/{channel}"
            webbrowser.open(url)
            logger.info(f"🌐 Открыт: {url}")

        tk.Button(root, text="🌐 Открыть стрим", command=open_stream,
                 bg="#9146FF", fg="white", font=("Segoe UI", 11, "bold"),
                 padx=20, pady=8).pack(pady=10)
        tk.Button(root, text="✕ Закрыть", command=root.destroy,
                 bg="#333", fg="white", font=("Segoe UI", 10),
                 padx=15, pady=8).pack(pady=5)

        root.after(1000, open_stream)
        root.after(5000, lambda: root.destroy() if root else None)
        root.mainloop()
    except Exception as e:
        logger.error(f"Ошибка окна: {type(e).__name__}")

# --- Реальный API ---
def real_check(client_id: str, channel: str, known: set):
    if not client_id:
        return

    import requests
    oauth_token = os.getenv("TWITCH_OAUTH_TOKEN", "").strip()
    headers = {'Client-ID': client_id.strip()}
    if oauth_token:
        headers['Authorization'] = f'Bearer {oauth_token}'

    try:
        resp = requests.get("https://api.twitch.tv/helix/streams",
                          headers=headers,
                          params={'user_login': channel},
                          timeout=10)

        if resp.status_code != 200:
            return

        data = resp.json()
        for stream in data.get('data', []):
            if stream['id'] not in known:
                logger.info(f"✅ Стрим: {channel} — {stream['title']}")
                show_notification(f"🔴 {channel} начал стрим!", stream['title'])
                threading.Thread(target=show_preview_window, args=(channel,), daemon=True).start()
                known.add(stream['id'])

    except Exception as e:
        logger.error(f"Ошибка API: {type(e).__name__}")

# --- Основной цикл (ТОЛЬКО РЕАЛЬНЫЙ РЕЖИМ) ---
def monitor_loop(settings: dict, stop_event=None):
    channels = [ch for ch in settings['channels'] if validate_channel(ch)]
    if not channels:
        logger.error("Нет валидных каналов")
        return

    known = set()
    logger.info(f"✅ Запущено, каналы: {channels}")

    try:
        while True:
            if stop_event and stop_event.is_set():
                logger.info("⏹ Остановка по сигналу")
                break

            for ch in channels:
                real_check(settings['client_id'], ch, known)
            time.sleep(settings['poll_interval'])
    except KeyboardInterrupt:
        logger.info("⏹ Остановлено пользователем")

# --- Глобальная переменная ---
_stop_event = None

# --- GUI ---
def run_gui():
    global _stop_event
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except:
        logger.error("tkinter не установлен")
        settings = load_settings()
        monitor_loop(settings)
        return

    settings = load_settings()
    root = tk.Tk()
    root.title("🎮 Twitch Notifier")
    root.geometry("450x400")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="🔑 TWITCH_CLIENT_ID:").grid(row=0, column=0, sticky="w")
    client_id_var = tk.StringVar(value=settings.get('client_id', ''))
    ttk.Entry(frame, textvariable=client_id_var, width=40).grid(row=1, column=0, columnspan=2)

    ttk.Label(frame, text="📺 Каналы:").grid(row=2, column=0, sticky="w")
    channels_text = tk.Text(frame, width=40, height=6)
    channels_text.grid(row=3, column=0, columnspan=2)
    for ch in settings.get('channels', []):
        channels_text.insert(tk.END, ch + "\n")

    ttk.Label(frame, text="⏱ Интервал (сек):").grid(row=4, column=0, sticky="w")
    interval_var = tk.IntVar(value=settings.get('poll_interval', 30))
    ttk.Spinbox(frame, from_=10, to=300, textvariable=interval_var, width=10).grid(row=4, column=1)

    # ✅ Демо-режим УДАЛЁН — только реальный мониторинг

    def save_and_start():
        global _stop_event
        raw = channels_text.get("1.0", tk.END).splitlines()
        channels = [c.strip().lower() for c in raw if c.strip()]
        valid = [c for c in channels if validate_channel(c)]

        if not valid:
            messagebox.showerror("Ошибка", "Нет валидных каналов")
            return

        settings['channels'] = valid
        settings['client_id'] = client_id_var.get().strip()
        settings['poll_interval'] = interval_var.get()
        save_settings(settings)

        root.withdraw()
        _stop_event = threading.Event()
        monitor_thread = threading.Thread(target=monitor_loop, args=(settings, _stop_event), daemon=False)
        monitor_thread.start()

        show_notification("✅ Запущено!", "Отслеживание стримов активно")

        status_label = ttk.Label(frame, text="🟢 Программа работает в фоне", foreground="#00ff00")
        status_label.grid(row=7, column=0, columnspan=2, pady=5)

        exit_btn = ttk.Button(frame, text="🚪 Выйти из программы", command=lambda: root.destroy())
        exit_btn.grid(row=8, column=0, columnspan=2, pady=10)

    ttk.Button(frame, text="💾 Сохранить и Запустить", command=save_and_start).grid(row=6, column=0, columnspan=2)
    root.mainloop()

    if _stop_event:
        _stop_event.set()
    logger.info("👋 Программа завершена")

# === ЗАПУСК ===
if __name__ == "__main__":
    logger.info("🚀 Twitch Stream Notifier — Production Edition")
    try:
        run_gui()
    except KeyboardInterrupt:
        logger.info("👋 Остановлено")
        if _stop_event:
            _stop_event.set()
        import sys
        sys.exit(0)
