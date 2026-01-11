# logic/status_manager.py
from typing import List
from core.unit.unit import Unit
from logic.statuses.status_definitions import STATUS_REGISTRY


class StatusManager:
    @staticmethod
    def process_turn_end(unit: 'Unit') -> List[str]:
        """
        Обрабатывает конец раунда для статусов (спадание, эффекты).
        """
        logs = []

        # Функция-обертка для логов, чтобы передавать её в on_round_end
        def log_wrapper(msg):
            logs.append(msg)

        active_ids = list(unit._status_effects.keys())

        for status_id in active_ids:
            if status_id not in unit._status_effects: continue

            instances_start = unit._status_effects[status_id]
            total_stack = sum(i["amount"] for i in instances_start)

            if status_id in STATUS_REGISTRY and total_stack > 0:
                handler = STATUS_REGISTRY[status_id]

                # === [ИЗМЕНЕНО] Вызываем on_round_end ===
                # Передаем stack через kwargs
                if hasattr(handler, "on_round_end"):
                    handler.on_round_end(unit, log_wrapper, stack=total_stack)

            # Проверка существования после хендлера
            if status_id not in unit._status_effects: continue

            # Уменьшение длительности (Decay)
            current_instances = unit._status_effects[status_id]
            next_instances = []

            for item in current_instances:
                item["duration"] -= 1
                if item["duration"] > 0:
                    next_instances.append(item)
                # Если длительность 0 - удаляется

            if next_instances:
                unit._status_effects[status_id] = next_instances
            else:
                del unit._status_effects[status_id]

        # Обработка Delayed (без изменений)
        if unit.delayed_queue:
            remaining = []
            for item in unit.delayed_queue:
                item["delay"] -= 1
                if item["delay"] <= 0:
                    unit.add_status(item["name"], item["amount"], duration=item["duration"])
                    logs.append(f"⏰ {item['name'].capitalize()} activated!")
                else:
                    remaining.append(item)
            unit.delayed_queue = remaining

        return logs