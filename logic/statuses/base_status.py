from logic.base_effect import BaseEffect
from core.logging import logger, LogLevel

class StatusEffect(BaseEffect):
    """
    Базовый класс для статусов.
    Наследует весь интерфейс от BaseEffect.
    """
    id = "base_status"

    # Можно добавить специфичные для статусов методы, если они появятся,
    # но пока BaseEffect покрывает всё.
    def on_use(self, unit, card):
        """
        Триггер при использовании (если статус подразумевает какое-то действие).
        """
        # Логируем факт вызова метода (полезно для отладки активных статусов/предметов)
        logger.log(f"Status {self.id} on_use triggered for {unit.name}", LogLevel.VERBOSE, "Status")
        pass