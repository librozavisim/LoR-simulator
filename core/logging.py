import os
import streamlit as st
from enum import IntEnum
from datetime import datetime

# Путь к файлу полного лога
LOG_FILE_PATH = "data/logs/full_battle_log.txt"


class LogLevel(IntEnum):
    """
    Уровни детализации логов.
    """
    MINIMAL = 1  # Уровень 1: Только важные итоги (Нанесенный урон, Смерть, Результат столкновения)
    NORMAL = 2  # Уровень 2: Стандарт (Применение карт, Наложение статусов, Значения кубиков)
    VERBOSE = 3  # Уровень 3: Полный (Триггеры пассивок, Кулдауны, Детали расчетов, Начало фаз)


class BattleLogger:
    """
    Система логгирования.
    - Пишет ВСЕ логи в файл data/logs/full_battle_log.txt.
    - Сохраняет логи в st.session_state для отображения в UI с фильтрацией.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BattleLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Инициализация происходит один раз при создании
        if not hasattr(self, 'initialized'):
            self.ensure_log_dir()
            # При первом запуске (или перезагрузке сервера) можно отбить начало сессии
            # Но файл мы будем очищать только по команде clear(), чтобы сохранять историю между реранами
            self.initialized = True

    def ensure_log_dir(self):
        """Создает папку для логов, если её нет."""
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    def log(self, message: str, level: LogLevel = LogLevel.NORMAL, category: str = "Info"):
        """
        Основной метод записи лога.

        Args:
            message (str): Текст сообщения.
            level (LogLevel): Важность (MINIMAL, NORMAL, VERBOSE).
            category (str): Категория (Combat, Effect, System, Dice...).
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Часы:Минуты:Секунды.Миллисекунды

        # 1. Запись в файл (Пишем ВСЕГДА всё подряд для дебага)
        # Формат: [TIME] [LEVEL] [CATEGORY] Message
        log_entry_str = f"[{timestamp}] [{level.name:<7}] [{category}] {message}\n"

        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry_str)
        except Exception as e:
            print(f"Logger File Error: {e}")

        # 2. Запись в память (Session State) для UI
        if 'battle_log_storage' not in st.session_state:
            st.session_state['battle_log_storage'] = []

        # Сохраняем объект лога
        ui_entry = {
            "id": len(st.session_state['battle_log_storage']),
            "time": timestamp,
            "level": level,
            "category": category,
            "message": message
        }

        st.session_state['battle_log_storage'].append(ui_entry)

    def clear(self):
        """
        Очищает логи в памяти и перезаписывает файл (например, при кнопке Reset Battle).
        """
        st.session_state['battle_log_storage'] = []

        try:
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(f"=== BATTLE LOG CLEARED: {datetime.now()} ===\n")
        except Exception as e:
            print(f"Logger Clear Error: {e}")

    def get_logs_for_ui(self, filter_level: LogLevel):
        """
        Возвращает список логов для отображения, фильтруя по уровню.
        Пример: Если выбран NORMAL (2), покажет MINIMAL (1) и NORMAL (2).
        """
        if 'battle_log_storage' not in st.session_state:
            return []

        return [
            entry for entry in st.session_state['battle_log_storage']
            if entry['level'] <= filter_level
        ]


# Глобальный экземпляр логгера для импорта в других файлах
logger = BattleLogger()