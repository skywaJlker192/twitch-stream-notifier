#!/usr/bin/env python3
"""
Проверка безопасности проекта (аналог check.sh для Rust).
Соответствует п.10: статический анализ, аудит, поиск секретов.
"""

import subprocess
import sys
import os
import re

def run(cmd: str, desc: str) -> bool:
    print(f"🔍 {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"❌ {desc} FAILED:")
            print(result.stderr.strip() or result.stdout.strip())
            return False
        else:
            print(f"✅ {desc} OK")
            return True
    except Exception as e:
        print(f"❌ {desc} ERROR: {e}")
        return False

def check_no_hardcoded_secrets():
    """П.10: grep по коду на секреты"""
    print("🔍 Поиск хардкод-секретов в .py...")
    try:
        with open("notifier.py", "r", encoding="utf-8") as f:
            content = f.read()
        patterns = [r"password", r"token", r"secret", r"client_secret"]
        found = []
        for pat in patterns:
            if re.search(pat, content, re.IGNORECASE):
                found.append(pat)
        if found:
            print(f"❌ Найдены подозрительные строки: {found}")
            return False
        print("✅ Секреты не найдены в коде")
        return True
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False

def main():
    ok = True

    ok &= check_no_hardcoded_secrets()
    ok &= run("pip install --upgrade pip-audit && pip-audit -r requirements.txt", "Проверка уязвимостей (pip-audit)")
    ok &= run("pip install flake8 && flake8 notifier.py tests/", "Проверка стиля (flake8)")

    if ok:
        print("\n🎉 Все проверки безопасности пройдены!")
    else:
        print("\n⚠️  Некоторые проверки не пройдены — не рекомендуется релиз.")
        sys.exit(1)

if __name__ == "__main__":
    main()
