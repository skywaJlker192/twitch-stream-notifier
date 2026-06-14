#!/usr/bin/env python3
"""Получение OAuth токена для Twitch API"""
import requests
import json

# Твои данные из консоли разработчика
CLIENT_ID = "tkmuvk8h2fjb3ivn8506kcshu1ped"
CLIENT_SECRET = "14ieq3qxd37wjpsq9probpma6d0bse"  # <-- Проверь, что это последний секрет!

def get_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, params=params)
        data = response.json()

        if response.status_code == 200:
            token = data["access_token"]
            print(f"✅ Успех! Твой OAuth токен:\n{token}")
            print(f"\n📋 Добавь это в файл .env:")
            print(f"TWITCH_OAUTH_TOKEN={token}")
            return token
        else:
            print(f"❌ Ошибка {response.status_code}: {data}")
            if response.status_code == 400:
                print("💡 Возможные причины:")
                print("   1. Неверный Client Secret (попробуй сгенерировать новый)")
                print("   2. Приложение отозвано в консоли Twitch")
                print("   3. Лишние пробелы в ключах")
            return None
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

if __name__ == "__main__":
    get_token()
