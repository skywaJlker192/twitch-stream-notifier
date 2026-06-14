#!/usr/bin/env python3
"""Диагностика Twitch API"""
import requests
import json

CLIENT_ID = "token"
CHANNEL = "channel"

print(f"🔍 Тестируем API для канала: {CHANNEL}")
print(f"🔑 Client ID: {CLIENT_ID[:10]}...")
print()

# Пробуем разные варианты заголовков
test_cases = [
    {"name": "Только Client-ID", "headers": {"Client-ID": CLIENT_ID}},
    {"name": "Client-ID + User-Agent", "headers": {"Client-ID": CLIENT_ID, "User-Agent": "TwitchNotifier/1.0"}},
]

for case in test_cases:
    print(f"📡 Тест: {case['name']}")
    try:
        resp = requests.get(
            "https://api.twitch.tv/helix/streams",
            headers=case["headers"],
            params={"user_login": CHANNEL},
            timeout=10
        )
        print(f"   Статус: {resp.status_code}")
        if resp.status_code != 200:
            print(f"   Ответ: {resp.text[:200]}")
        else:
            data = resp.json()
            streams = data.get("data", [])
            if streams:
                print(f"   ✅ Стрим найден: {streams[0]['title']}")
            else:
                print(f"   ℹ️  Стримов нет (канал офлайн)")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    print()
