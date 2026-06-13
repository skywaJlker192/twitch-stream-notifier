# gui_config.py
import tkinter as tk
from tkinter import ttk, messagebox
import settings_manager
import threading
import notifier_core  # Новый файл для основной логики

class SettingsWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Настройки Twitch Notifier")
        self.root.geometry("500x400")

        self.settings = settings_manager.load_settings()

        # --- GUI ---
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="TWITCH_CLIENT_ID:").grid(column=0, row=0, sticky=tk.W, pady=2)
        self.client_id_var = tk.StringVar(value=self.settings.get("twitch_client_id", ""))
        self.client_id_entry = ttk.Entry(frame, textvariable=self.client_id_var, width=50)
        self.client_id_entry.grid(column=0, row=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(frame, text="Каналы (по одному в строке):").grid(column=0, row=2, sticky=(tk.W, tk.N), pady=(10, 2))
        self.channels_text = tk.Text(frame, width=40, height=8)
        self.channels_text.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        channels_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.channels_text.yview)
        channels_scrollbar.grid(column=2, row=3, sticky=(tk.N, tk.S))
        self.channels_text.configure(yscrollcommand=channels_scrollbar.set)

        # Вставляем каналы из настроек
        for ch in self.settings.get("channels", []):
            self.channels_text.insert(tk.END, ch + "\n")

        ttk.Label(frame, text="Интервал проверки (сек):").grid(column=0, row=4, sticky=tk.W, pady=2)
        self.interval_var = tk.IntVar(value=self.settings.get("poll_interval", 30))
        self.interval_spinbox = ttk.Spinbox(frame, from_=10, to=300, textvariable=self.interval_var, width=10)
        self.interval_spinbox.grid(column=1, row=4, sticky=tk.W, pady=2)

        self.save_and_start_button = ttk.Button(frame, text="Сохранить и Запустить", command=self.save_and_start)
        self.save_and_start_button.grid(column=0, row=5, pady=10)

        self.status_label = ttk.Label(frame, text="Готов.", foreground="green")
        self.status_label.grid(column=0, row=6, sticky=tk.W)

    def save_and_start(self):
        """Сохранить настройки и запустить отслеживание в отдельном потоке."""
        try:
            client_id = self.client_id_var.get().strip()
            if not client_id:
                messagebox.showwarning("Предупреждение", "TWITCH_CLIENT_ID не указан. Работа будет невозможна.")
                return # Не выходим, просто не запускаем

            channels_raw = self.channels_text.get("1.0", tk.END).strip()
            channels_list = [ch.strip().lower() for ch in channels_raw.splitlines() if ch.strip()]
            poll_interval = self.interval_var.get()

            # Сохраняем
            self.settings["twitch_client_id"] = client_id
            self.settings["channels"] = channels_list
            self.settings["poll_interval"] = poll_interval
            settings_manager.save_settings(self.settings)

            self.status_label.config(text="Сохранено. Запуск...", foreground="orange")

            # Запускаем основной цикл в отдельном потоке
            thread = threading.Thread(target=notifier_core.run_monitoring, kwargs={
                'channels': channels_list,
                'interval': poll_interval,
                'client_id': client_id
            }, daemon=True)
            thread.start()

            self.status_label.config(text="Запущено (проверьте консоль)", foreground="blue")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить или запустить:\n{e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SettingsWindow()
    app.run()
