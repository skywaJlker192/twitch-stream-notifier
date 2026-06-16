#!/usr/bin/env python3
"""
Twitch Stream Notifier — Production Edition v2.0
- Автообновление OAuth токена через Client Credentials Flow
- Регистронезависимые имена каналов
- Детальное логирование всех ошибок
- Гарантированная работа в фоне
"""

import os, sys, re, json, time, logging, threading, webbrowser
from pathlib import Path

# === Определение папки приложения (для exe и скрипта) ===
if getattr(sys, 'frozen', False):
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# === Загрузка .env из папки приложения ===
ENV_FILE = APP_DIR / ".env"
if ENV_FILE.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ENV_FILE)
else:
    print(f"❌ .env НЕ НАЙДЕН в: {ENV_FILE}")

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(APP_DIR / "notifier.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 🌐 ЛОКАЛИЗАЦИЯ ====================

CURRENT_LANG = "ru"

TRANSLATIONS = {
    "ru": {
        "window_title": "🎮 Twitch Notifier",
        "client_id_label": "🔑 TWITCH_CLIENT_ID:",
        "channels_label": "📺 Каналы:",
        "interval_label": "⏱ Интервал (сек):",
        "save_btn": "💾 Сохранить и Запустить",
        "exit_btn": "🚪 Выйти из программы",
        "lang_btn": "🌐 English",
        "working_status": "🟢 Программа работает в фоне",
        "error_title": "Ошибка",
        "error_no_channels": "Нет валидных каналов (a-zA-Z0-9_, 2-25 символов)",
        "started_title": "✅ Запущено!",
        "started_msg": "Отслеживание стримов активно",
        "preview_stream_started": "✅ Стрим запущен!",
        "preview_opening": "Открываю стрим в браузере...",
        "preview_open_btn": "🌐 Открыть стрим",
        "preview_close_btn": "✕ Закрыть",
        "notif_started_title": "начал стрим!",
        "log_no_channels": "Нет валидных каналов",
        "log_started": "✅ Запущено, каналы: {channels}",
        "log_stopped_signal": "⏹ Остановка по сигналу",
        "log_stopped_user": "⏹ Остановлено пользователем",
        "log_stream": "✅ Стрим: {channel} — {title}",
        "log_opened": "🌐 Открыт: {url}",
        "log_finished": "👋 Программа завершена",
    },
    "en": {
        "window_title": "🎮 Twitch Notifier",
        "client_id_label": "🔑 TWITCH_CLIENT_ID:",
        "channels_label": "📺 Channels:",
        "interval_label": "⏱ Interval (sec):",
        "save_btn": "💾 Save & Start",
        "exit_btn": "🚪 Exit program",
        "lang_btn": "🌐 Русский",
        "working_status": "🟢 Program is running in background",
        "error_title": "Error",
        "error_no_channels": "No valid channels (a-zA-Z0-9_, 2-25 chars)",
        "started_title": "✅ Started!",
        "started_msg": "Stream monitoring active",
        "preview_stream_started": "✅ Stream started!",
        "preview_opening": "Opening stream in browser...",
        "preview_open_btn": "🌐 Open stream",
        "preview_close_btn": "✕ Close",
        "notif_started_title": "started streaming!",
        "log_no_channels": "No valid channels",
        "log_started": "✅ Started, channels: {channels}",
        "log_stopped_signal": "⏹ Stopped by signal",
        "log_stopped_user": "⏹ Stopped by user",
        "log_stream": "✅ Stream: {channel} — {title}",
        "log_opened": "🌐 Opened: {url}",
        "log_finished": "👋 Program finished",
    }
}

def tr(key, **kwargs):
    text = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["ru"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text

def toggle_language():
    global CURRENT_LANG
    CURRENT_LANG = "en" if CURRENT_LANG == "ru" else "ru"
    logger.info(f"🌐 Язык переключен: {CURRENT_LANG.upper()}")
    return CURRENT_LANG

# --- Настройки ---
SETTINGS_FILE = APP_DIR / "settings.json"
DEFAULT_SETTINGS = {
    "poll_interval": 30,
    "client_id": os.getenv("TWITCH_CLIENT_ID", ""),
    "client_secret": os.getenv("TWITCH_CLIENT_SECRET", ""),
    "language": "ru"
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

# --- Валидация (регистронезависимая) ---
def validate_channel(name: str) -> bool:
    """Проверяет валидность имени канала"""
    return bool(re.match(r'^[a-zA-Z0-9_]{2,25}$', name))

def normalize_channel(name: str) -> str:
    """Приводит имя канала к нижнему регистру"""
    return name.strip().lower()

# --- Уведомления ---
def show_notification(title: str, message: str):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name='Twitch Notifier', timeout=10)
    except:
        logger.warning("plyer не установлен")
        print(f"[🔔] {title}: {message}")

# --- Открытие стрима в браузере ---
def open_stream_in_browser(channel: str):
    """Открывает стрим в браузере"""
    try:
        url = f"https://twitch.tv/{channel}"
        webbrowser.open(url)
        logger.info(tr("log_opened", url=url))
    except Exception as e:
        logger.error(f"Ошибка открытия браузера: {type(e).__name__}")

# --- Окно превью ---
def show_preview_window(channel: str):
    """Открывает стрим в браузере + показывает окно"""
    try:
        if not validate_channel(channel):
            return

        # СНАЧАЛА открываем браузер — это ГЛАВНОЕ!
        open_stream_in_browser(channel)

        # ПОТОМ пытаемся показать окно
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title(f"🔴 {channel} — LIVE")
            root.geometry("400x250")
            root.configure(bg="#1a1a1a")
            root.attributes("-topmost", True)

            tk.Label(root, text=f"🎮 {channel}", fg="#9146FF", bg="#1a1a1a",
                    font=("Segoe UI", 18, "bold")).pack(pady=15)
            tk.Label(root, text=tr("preview_stream_started"), fg="#00ff00", bg="#1a1a1a",
                    font=("Segoe UI", 12)).pack(pady=5)
            tk.Label(root, text=tr("preview_opening"),
                    fg="#888", bg="#1a1a1a").pack(pady=10)

            tk.Button(root, text=tr("preview_open_btn"),
                     command=lambda: open_stream_in_browser(channel),
                     bg="#9146FF", fg="white", font=("Segoe UI", 11, "bold"),
                     padx=20, pady=8).pack(pady=10)
            tk.Button(root, text=tr("preview_close_btn"), command=root.destroy,
                     bg="#333", fg="white", font=("Segoe UI", 10),
                     padx=15, pady=8).pack(pady=5)

            root.after(5000, lambda: root.destroy() if root else None)
            root.mainloop()
        except Exception as e:
            logger.error(f"Ошибка окна превью: {type(e).__name__}")
    except Exception as e:
        logger.error(f"Ошибка show_preview_window: {type(e).__name__}")

# ==================== 🔐 АВТООБНОВЛЕНИЕ ТОКЕНА ====================

def get_app_access_token(client_id: str, client_secret: str) -> str:
    """
    Получает App Access Token через Client Credentials Flow.
    Токен действует ~60 дней, но мы обновляем его при каждом запуске.
    """
    if not client_id or not client_secret:
        logger.warning("⚠️ Client ID или Client Secret не заданы — автообновление токена недоступно")
        return ""

    import requests
    try:
        resp = requests.post("https://id.twitch.tv/oauth2/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }, timeout=10)

        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            expires_in = resp.json().get("expires_in", 0)
            logger.info(f"✅ Получен новый App Access Token (действителен {expires_in // 3600} часов)")
            return token
        else:
            logger.error(f"❌ Ошибка получения токена: HTTP {resp.status_code} — {resp.text[:200]}")
            return ""
    except Exception as e:
        logger.error(f"❌ Ошибка сети при получении токена: {type(e).__name__}")
        return ""

# ==================== 🔍 ПРОВЕРКА СТРИМА ====================

def real_check(client_id: str, channel: str, known: set, stats: dict):
    """Проверка стрима с детальным логированием"""
    if not client_id:
        logger.error(f"❌ Client ID пустой для {channel}!")
        return

    import requests
    oauth_token = os.getenv("TWITCH_OAUTH_TOKEN", "").strip()
    headers = {'Client-ID': client_id.strip()}
    if oauth_token:
        headers['Authorization'] = f'Bearer {oauth_token}'

    # 🔥 Нормализуем канал к lowercase
    channel_lower = normalize_channel(channel)

    try:
        resp = requests.get("https://api.twitch.tv/helix/streams",
                          headers=headers,
                          params={'user_login': channel_lower},
                          timeout=10)

        # 🔥 ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ОШИБОК
        if resp.status_code == 401:
            logger.error(f"❌ {channel}: ОШИБКА 401 — OAuth токен невалиден!")
            logger.error(f"💡 Получите новый токен: https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri=http://localhost:3000&response_type=token")
            stats['errors'] += 1
            if stats['errors'] % 10 == 1:
                show_notification(
                    "⚠️ Ошибка Twitch API!",
                    "OAuth токен недействителен. Получите новый токен и обновите .env"
                )
            return
        elif resp.status_code == 429:
            logger.warning(f"⚠️ {channel}: Rate limit (429) — слишком много запросов")
            return
        elif resp.status_code != 200:
            logger.error(f"❌ {channel}: HTTP {resp.status_code} — {resp.text[:100]}")
            stats['errors'] += 1
            return

        data = resp.json()
        streams = data.get('data', [])

        if streams:
            stream = streams[0]
            logger.info(f"🟢 {channel}: ОНЛАЙН — {stream['title'][:50]}...")

            if stream['id'] not in known:
                logger.info(tr("log_stream", channel=channel, title=stream['title']))
                show_notification(f"🔴 {channel} {tr('notif_started_title')}", stream['title'])
                # Запускаем в отдельном потоке
                threading.Thread(target=show_preview_window, args=(channel,), daemon=True).start()
                known.add(stream['id'])
        else:
            logger.info(f"⚪ {channel}: офлайн")

    except requests.Timeout:
        logger.error(f"⏱ {channel}: Таймаут запроса к Twitch API")
    except requests.ConnectionError:
        logger.error(f"🌐 {channel}: Нет подключения к интернету")
    except Exception as e:
        logger.error(f"💥 {channel}: {type(e).__name__} — {e}")

# ==================== 🔄 ОСНОВНОЙ ЦИКЛ ====================

def monitor_loop(settings: dict, stop_event=None):
    # 🔥 ЧИТАЕМ client_secret ПРЯМО ИЗ .env, а не из settings!
    client_id = os.getenv("TWITCH_CLIENT_ID", "").strip()
    client_secret = os.getenv("TWITCH_CLIENT_SECRET", "").strip()

    if client_id and client_secret:
        logger.info("🔄 Попытка автообновления OAuth токена...")
        fresh_token = get_app_access_token(client_id, client_secret)
        if fresh_token:
            os.environ["TWITCH_OAUTH_TOKEN"] = fresh_token
            logger.info("✅ OAuth токен обновлён автоматически")
        else:
            logger.warning("⚠️ Не удалось обновить токен автоматически")
    else:
        logger.warning("⚠️ TWITCH_CLIENT_SECRET не задан в .env")

    # ... остальной код без изменений

    # Валидация и нормализация каналов
    raw_channels = settings.get('channels', [])
    channels = []
    for ch in raw_channels:
        ch_normalized = normalize_channel(ch)
        if validate_channel(ch_normalized):
            channels.append(ch_normalized)
        else:
            logger.warning(f"⚠️ Невалидный канал пропущен: {ch}")

    if not channels:
        logger.error(tr("log_no_channels"))
        return

    known = set()
    stats = {'cycles': 0, 'errors': 0}
    logger.info(tr("log_started", channels=channels))
    logger.info(f"📊 Интервал опроса: {settings['poll_interval']} сек")

    try:
        while True:
            if stop_event and stop_event.is_set():
                logger.info(tr("log_stopped_signal"))
                break

            stats['cycles'] += 1
            logger.info(f"═══ Цикл проверки №{stats['cycles']} ═══")

            for ch in channels:
                real_check(client_id, ch, known, stats)

            # Показываем статус каждые 10 циклов
            if stats['cycles'] % 10 == 0:
                logger.info(f"📈 Статистика: циклов={stats['cycles']}, ошибок={stats['errors']}, стримов={len(known)}")

            time.sleep(settings['poll_interval'])
    except KeyboardInterrupt:
        logger.info(tr("log_stopped_user"))

# --- Глобальная переменная ---
_stop_event = None

# ==================== 🎨 GUI ====================

def run_gui():
    global _stop_event, CURRENT_LANG
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except:
        logger.error("tkinter не установлен")
        settings = load_settings()
        monitor_loop(settings)
        return

    settings = load_settings()
    CURRENT_LANG = settings.get('language', 'ru')

    root = tk.Tk()
    root.title(tr("window_title"))
    root.geometry("450x450")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill=tk.BOTH, expand=True)

    # Кнопка переключения языка
    lang_btn = ttk.Button(frame, text=tr("lang_btn"),
                         command=lambda: update_language(lang_btn, save_btn, status_label, exit_btn,
                                                        client_id_lbl, channels_lbl, interval_lbl, root))
    lang_btn.grid(row=0, column=1, sticky="e", pady=(0, 10))

    # Client ID
    client_id_lbl = ttk.Label(frame, text=tr("client_id_label"))
    client_id_lbl.grid(row=1, column=0, sticky="w")
    client_id_var = tk.StringVar(value=settings.get('client_id', ''))
    ttk.Entry(frame, textvariable=client_id_var, width=40).grid(row=2, column=0, columnspan=2)

    # Каналы
    channels_lbl = ttk.Label(frame, text=tr("channels_label"))
    channels_lbl.grid(row=3, column=0, sticky="w")
    channels_text = tk.Text(frame, width=40, height=6)
    channels_text.grid(row=4, column=0, columnspan=2)
    for ch in settings.get('channels', []):
        channels_text.insert(tk.END, ch + "\n")

    # Интервал
    interval_lbl = ttk.Label(frame, text=tr("interval_label"))
    interval_lbl.grid(row=5, column=0, sticky="w")
    interval_var = tk.IntVar(value=settings.get('poll_interval', 30))
    ttk.Spinbox(frame, from_=10, to=300, textvariable=interval_var, width=10).grid(row=5, column=1)

    # Кнопка запуска
    save_btn = ttk.Button(frame, text=tr("save_btn"))
    save_btn.grid(row=6, column=0, columnspan=2, pady=10)

    # Статус и выход
    status_label = ttk.Label(frame, text="", foreground="#00ff00")
    exit_btn = ttk.Button(frame, text="")

    def save_and_start():
        global _stop_event
        raw = channels_text.get("1.0", tk.END).splitlines()
        channels = [normalize_channel(c) for c in raw if c.strip()]
        valid = [c for c in channels if validate_channel(c)]

        if not valid:
            messagebox.showerror(tr("error_title"), tr("error_no_channels"))
            return

        settings['channels'] = valid
        settings['client_id'] = client_id_var.get().strip()
        settings['poll_interval'] = interval_var.get()
        settings['language'] = CURRENT_LANG
        save_settings(settings)

        root.withdraw()
        _stop_event = threading.Event()
        monitor_thread = threading.Thread(target=monitor_loop, args=(settings, _stop_event), daemon=False)
        monitor_thread.start()

        show_notification(tr("started_title"), tr("started_msg"))

        status_label.config(text=tr("working_status"))
        status_label.grid(row=7, column=0, columnspan=2, pady=5)

        exit_btn.config(text=tr("exit_btn"), command=lambda: root.destroy())
        exit_btn.grid(row=8, column=0, columnspan=2, pady=10)

    save_btn.config(command=save_and_start)
    root.mainloop()

    if _stop_event:
        _stop_event.set()
    logger.info(tr("log_finished"))

def update_language(lang_btn, save_btn, status_label, exit_btn,
                   client_id_lbl, channels_lbl, interval_lbl, root):
    global CURRENT_LANG
    CURRENT_LANG = toggle_language()

    root.title(tr("window_title"))
    lang_btn.config(text=tr("lang_btn"))
    client_id_lbl.config(text=tr("client_id_label"))
    channels_lbl.config(text=tr("channels_label"))
    interval_lbl.config(text=tr("interval_label"))
    save_btn.config(text=tr("save_btn"))

    if status_label.cget("text"):
        status_label.config(text=tr("working_status"))
        exit_btn.config(text=tr("exit_btn"))

# === ЗАПУСК ===
if __name__ == "__main__":
    logger.info("🚀 Twitch Stream Notifier v2.0 — Production Edition")
    try:
        run_gui()
    except KeyboardInterrupt:
        logger.info(tr("log_stopped_user"))
        if _stop_event:
            _stop_event.set()
        sys.exit(0)
