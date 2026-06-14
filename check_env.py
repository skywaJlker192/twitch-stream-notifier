#!/usr/bin/env python3
"""Проверка загрузки переменных окружения"""
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env

client_id = os.getenv("TWITCH_CLIENT_ID", "НЕ НАЙДЕН")
oauth_token = os.getenv("TWITCH_OAUTH_TOKEN", "НЕ НАЙДЕН")

print("🔍 Проверка переменных:")
print(f"TWITCH_CLIENT_ID: {client_id[:10] if len(client_id) > 10 else client_id}...")
print(f"TWITCH_OAUTH_TOKEN: {oauth_token[:10] if len(oauth_token) > 10 else oauth_token}...")

if client_id == "НЕ НАЙДЕН" or oauth_token == "НЕ НАЙДЕН":
    print("❌ Переменные не загружены! Проверь .env и load_dotenv()")
else:
    print("✅ Переменные загружены!")
