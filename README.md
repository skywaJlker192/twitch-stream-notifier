# 👾 Twitch Stream Notifier

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Twitch API](https://img.shields.io/badge/Twitch-API-9146FF?style=for-the-badge&logo=twitch&logoColor=white)](https://dev.twitch.tv/docs/api)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)]()
[![Release](https://img.shields.io/badge/Release-v1.0.0-9146FF?style=for-the-badge)](https://github.com/skywaJlker192/Following_steamers/releases)

**Автоматический монитор стримов Twitch с уведомлениями и авто-открытием браузера**

[📥 Скачать .exe](https://github.com/skywaJlker192/Following_steamers/releases/latest) •
[📖 Документация](#-быстрый-старт) •
[🐛 Сообщить о проблеме](https://github.com/skywaJlker192/Following_steamers/issues) •
[💡 Предложить идею](https://github.com/skywaJlker192/Following_steamers/issues/new)

</div>

---

## 📖 Оглавление

- [✨ Возможности](#-возможности)
- [⚡ Быстрый старт](#-быстрый-старт)
- [🔑 Получение Twitch API ключей](#-получение-twitch-api-ключей)
- [🛠 Для разработчиков](#-для-разработчиков)
- [🔐 Безопасность](#-безопасность)
- [📁 Структура проекта](#-структура-проекта)
- [🐛 Решение проблем](#-решение-проблем)
- [📄 Лицензия](#-лицензия)

---

## ✨ Возможности

<table>
<tr>
<td width="50%">

### 🎯 Основные функции
- 🔔 **Мгновенные уведомления** при старте стрима
- 🌐 **Авто-открытие браузера** со стримом через 1 сек
- 🔄 **Фоновая работа** после скрытия окна
- 🌐 **Два языка**: Русский / English
- ⏱ **Гибкий интервал** проверки (10-300 сек)
- 🖼️ **Красивые окна** с информацией о канале

</td>
<td width="50%">

### 🔐 Безопасность
- ✅ OAuth 2.0 аутентификация
- ✅ Секреты в `.env` (не в коде)
- ✅ Белая валидация каналов
- ✅ Безопасное логирование
- ✅ Защита от rate limiting
- ✅ Параметризованные запросы

</td>
</tr>
</table>

---

### Как это работает:

```
1. Запускаешь TwitchNotifier.exe
2. Настраиваешь каналы для отслеживания
3. Сворачиваешь окно — программа работает в фоне
4. Когда стример начинает стрим:
   ├─ 📱 Системное уведомление
   ├─ 🖼️ Окно превью с информацией
   └─ 🌐 Браузер автоматически открывает стрим
```

---

## ⚡ Быстрый старт

### 📥 Шаг 1: Скачай приложение

Перейди в [Releases](https://github.com/skywaJlker192/Following_steamers/releases/download/v2.0.0/TwitchNotifier.exe) и скачай **`TwitchNotifier.exe`** из последнего релиза.

> 💡 **Совет:** Создай отдельную папку для программы, например `C:\TwitchNotifier\`

### 🔑 Шаг 2: Получи Twitch API ключи

См. подробную инструкцию в разделе [Получение Twitch API ключей](#-получение-twitch-api-ключей).

### 📝 Шаг 3: Создай файл `.env`

В папке с `TwitchNotifier.exe` создай файл **`.env`** (именно с точкой в начале, без расширения!) и вставь:

```env
TWITCH_CLIENT_ID=твой_client_id
TWITCH_OAUTH_TOKEN=твой_oauth_токен
```

> ⚠️ **Важно:** Файл должен называться именно `.env`, а не `env.txt` или `env`!

### 🚀 Шаг 4: Запусти приложение

Дважды кликни по **`TwitchNotifier.exe`** — готово! 🎉

---

## 🔑 Получение Twitch API ключей

### 1️⃣ Создай приложение на Twitch

1. Перейди на [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Войди в свой Twitch аккаунт
3. Нажми **"Register Your Application"**
4. Заполни форму:

| Поле | Значение |
|------|----------|
| **Name** | `twitch-notifier` (любое уникальное) |
| **OAuth Redirect URLs** | `http://localhost:3000` |
| **Category** | `Application Integration` |

5. Нажми **"Create"**
6. Скопируй **Client ID** (длинная строка)
7. Нажми **"Manage"** → **"New Secret"** → скопируй **Client Secret**

### 2️⃣ Получи OAuth токен

Открой в браузере эту ссылку, заменив `YOUR_CLIENT_ID` на свой Client ID:

```
https://id.twitch.tv/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000&response_type=token
```

1. Авторизуйся в Twitch (если нужно)
2. Нажми **"Authorize"**
3. Браузер перенаправит на `http://localhost:3000/#access_token=...`
4. Ты увидишь ошибку "Не удалось подключиться" — **это нормально!**
5. **Скопируй токен** из адресной строки (всё, что между `access_token=` и `&`)

### 3️⃣ Заполни `.env`

```env
TWITCH_CLIENT_ID=abc123xyz456...
TWITCH_OAUTH_TOKEN=def789uvw012...
```

---

## 🛠 Для разработчиков

### 📋 Требования

- Python 3.12+
- Git
- Windows 10/11

### 🚀 Установка

```bash
# Клонируй репозиторий
git clone https://github.com/skywaJlker192/Following_steamers.git
cd Following_steamers

# Создай виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установи зависимости
pip install -r requirements.txt
```

### ▶️ Запуск

```bash
# Создай .env файл (см. пример в .env.example)
# Запусти программу
python notifier.py
```

### 📦 Сборка в .exe

```bash
# Установи PyInstaller
pip install pyinstaller

# Собери exe
pyinstaller --onefile --windowed \
  --name "TwitchNotifier" \
  --hidden-import plyer.platforms.win.notification \
  --hidden-import plyer.platforms.win \
  --collect-all plyer \
  notifier.py

# Готовый exe будет в dist/TwitchNotifier.exe
```

### 📝 Структура кода

```python
notifier.py
├── load_dotenv()          # Загрузка .env
├── TRANSLATIONS           # Словарь переводов RU/EN
├── validate_channel()     # Валидация имён каналов
├── show_notification()    # Системные уведомления
├── show_preview_window()  # Окно превью стрима
├── real_check()           # Запрос к Twitch API
├── monitor_loop()         # Основной цикл мониторинга
└── run_gui()              # Графический интерфейс
```

---

## 🔐 Безопасность

Проект соответствует **10 ключевым требованиям безопасности**:

| № | Требование | Реализация |
|---|------------|------------|
| 1 | **Валидация ввода** | Белая валидация каналов `[a-zA-Z0-9_]{2,25}` |
| 2 | **Обработка ошибок** | `try/except`, логирование без утечки PII |
| 3 | **Аутентификация** | OAuth 2.0 Bearer Token |
| 4 | **Защита данных** | Параметризованные запросы, нет конкатенации |
| 5 | **Секреты** | Хранение в `.env`, не в коде |
| 6 | **Rate Limiting** | Интервал между запросами (по умолчанию 30 сек) |
| 7 | **Зависимости** | Стабильные версии в `requirements.txt` |
| 8 | **Тестирование** | Валидация ввода, обработка edge cases |
| 9 | **Документация** | Комментарии в коде, README |
| 10| **Git** | `.gitignore` для `.env`, `*.log`, `settings.json` |

---

## 📁 Структура проекта

```
Following_streamers/
│
├── notifier.py              # 🎯 Главный код приложения
├── README.md                # 📖 Документация (этот файл)
├── .gitignore               # 🔒 Правила игнорирования Git
├── requirements.txt         # 📦 Python зависимости
├── LICENSE                  # 📄 Лицензия MIT
├── .env.example             # 📝 Шаблон для .env
│
├── .env                     # 🔐 Секреты (НЕ коммитить!)
├── settings.json            # ⚙️ Настройки пользователя (НЕ коммитить!)
├── notifier.log             # 📝 Лог работы (НЕ коммитить!)
│
└── dist/                    # 📦 Папка сборки (НЕ коммитить!)
    └── TwitchNotifier.exe   # 🎮 Готовый exe файл
```

---

## 🐛 Решение проблем

### ❌ Ошибка `401 Unauthorized`

**Причина:** Неверный Client ID или OAuth токен.

**Решение:**
1. Проверь, что в `.env` указаны правильные значения
2. Убедись, что нет пробелов вокруг `=`
3. Получи новый OAuth токен (старый мог истечь)

### ❌ Ошибка `429 Too Many Requests`

**Причина:** Превышен лимит запросов к Twitch API.

**Решение:**
- Увеличь `poll_interval` до 60+ секунд в настройках
- Подожди 5 минут перед повторным запуском

### ❌ Не приходят уведомления

**Причина:** Не установлен `plyer` или отключены уведомления в системе.

**Решение:**
```bash
pip install plyer
```
Проверь настройки уведомлений в Windows: Параметры → Система → Уведомления.

### ❌ Окно не открывается

**Причина:** Не установлен `tkinter`.

**Решение:**
`tkinter` встроен в Python. Проверь:
```bash
python -m tkinter
```
Должно открыться тестовое окно.

### ❌ exe не запускается

**Причина:** Не установлен Visual C++ Redistributable.

**Решение:**
Скачай и установи [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).

### ❌ `.env` не читается

**Причина:** Файл называется неправильно.

**Решение:**
- Файл должен называться **`.env`** (с точкой в начале)
- Должен лежать **в той же папке**, что и exe
- Не должно быть расширения `.txt`

---

### 🚧 В разработке
- [ ] Иконка в системном трее
- [ ] Звуковые уведомления
- [ ] Статистика просмотров
- [ ] Тёмная/светлая тема


## 📊 Статистика проекта

<div align="center">

![GitHub repo size](https://img.shields.io/github/repo-size/skywaJlker192/Following_steamers)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/skywaJlker192/Following_streamers)
![GitHub issues](https://img.shields.io/github/issues/skywaJlker192/Following_steamers)
![GitHub pull requests](https://img.shields.io/github/issues-pr/skywaJlker192/Following_streamers)
![GitHub last commit](https://img.shields.io/github/last-commit/skywaJlker192/Following_steamers)

</div>

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT License** — см. файл [LICENSE](LICENSE) для подробностей.

```
MIT License

Copyright (c) 2026 Arkhip (skywaJlker192)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```


---

## 🙏 Благодарности

- [Twitch](https://www.twitch.tv/) — за отличную платформу и API
