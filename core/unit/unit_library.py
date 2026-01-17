# core/unit/unit_library.py
import os
import json
from core.unit.unit import Unit
from core.logging import logger, LogLevel  # [LOG] Импорт логгера


class UnitLibrary:
    _roster = {}
    DATA_PATH = "data/units"

    @classmethod
    def load_all(cls):
        """Загружает всех персонажей из JSON файлов в папке."""
        cls._roster = {}
        if not os.path.exists(cls.DATA_PATH):
            os.makedirs(cls.DATA_PATH, exist_ok=True)
            logger.log(f"Created directory: {cls.DATA_PATH}", LogLevel.VERBOSE, "System")
            return {}

        files = [f for f in os.listdir(cls.DATA_PATH) if f.endswith('.json')]
        logger.log(f"Loading units from {cls.DATA_PATH}...", LogLevel.VERBOSE, "System")

        loaded_count = 0
        for filename in files:
            path = os.path.join(cls.DATA_PATH, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    unit = Unit.from_dict(data)
                    cls._roster[unit.name] = unit
                    loaded_count += 1
            except Exception as e:
                logger.log(f"❌ Error loading {filename}: {e}", LogLevel.NORMAL, "System")

        if loaded_count > 0:
            logger.log(f"✔ Loaded {loaded_count} units into roster.", LogLevel.NORMAL, "System")

        return cls._roster

    @classmethod
    def save_unit(cls, unit: Unit):
        """Сохраняет одного персонажа в файл."""
        if not os.path.exists(cls.DATA_PATH):
            os.makedirs(cls.DATA_PATH, exist_ok=True)

        # Формируем имя файла из имени персонажа (безопасно)
        safe_name = "".join(c for c in unit.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        filename = f"{safe_name}.json"
        path = os.path.join(cls.DATA_PATH, filename)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(unit.to_dict(), f, indent=4, ensure_ascii=False)
            logger.log(f"💾 Saved unit: {unit.name} -> {path}", LogLevel.NORMAL, "System")
            # Обновляем кэш
            cls._roster[unit.name] = unit
            return True
        except Exception as e:
            logger.log(f"Error saving unit {unit.name}: {e}", LogLevel.NORMAL, "System")
            return False

    @classmethod
    def delete_unit(cls, unit_name):
        """Удаляет персонажа из памяти и с диска."""
        # 1. Удаляем из памяти
        if unit_name in cls._roster:
            del cls._roster[unit_name]

        # 2. Удаляем файл
        safe_name = "".join(c for c in unit_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        filename = f"{safe_name}.json"
        path = os.path.join(cls.DATA_PATH, filename)

        if os.path.exists(path):
            try:
                os.remove(path)
                logger.log(f"🗑️ Deleted unit file: {path}", LogLevel.NORMAL, "System")
                return True
            except Exception as e:
                logger.log(f"Error deleting unit file {path}: {e}", LogLevel.NORMAL, "System")
                return False
        return True

    @classmethod
    def get_roster(cls):
        return cls._roster