import random

from core.logging import logger, LogLevel


class SpeedRollMixin:
    """
    Отвечает за броски скорости и создание активных слотов.
    Требует наличия MechanicsIteratorMixin и методов проверки состояния.
    """

    def roll_speed_dice(self):
        """Генерация активных слотов на раунд."""
        self.active_slots = []
        self.counter_dice = []

        logger.log(f"🎲 Rolling Speed Dice for {self.name}", LogLevel.VERBOSE, "System")

        if self.is_dead():
            logger.log(f"{self.name} is dead, skipping roll.", LogLevel.VERBOSE, "System")
            return

        slot_penalty = self.get_status("slot_lock")
        if slot_penalty > 0:
            logger.log(f"{self.name} has slot penalty: -{slot_penalty}", LogLevel.NORMAL, "Status")

        total_potential_slots = len(self.computed_speed_dice)
        slots_to_roll = max(1, total_potential_slots - slot_penalty)

        speed_modifier = 0
        active_mechanics = list(self._iter_all_mechanics())

        # Сбор модификаторов скорости
        for effect in active_mechanics:
            if hasattr(effect, "get_speed_dice_value_modifier"):
                speed_modifier += effect.get_speed_dice_value_modifier(self)

        speed_rolls = []

        # 1. Основные слоты
        for i, (d_min, d_max) in enumerate(self.computed_speed_dice):
            if i >= slots_to_roll: break

            val = max(1, random.randint(int(d_min), int(d_max)) + speed_modifier)
            self.active_slots.append({
                'speed': val, 'card': None, 'target_slot': None, 'is_aggro': False
            })
            speed_rolls.append(val)

        # 2. Бонусные слоты (от эффектов)
        extra_dice_count = 0
        for effect in active_mechanics:
            if hasattr(effect, "get_speed_dice_bonus"):
                bonus = effect.get_speed_dice_bonus(self)
                if bonus > 0:
                    extra_dice_count += bonus
                    logger.log(f"Extra Speed Die from {getattr(effect, 'id', 'Unknown')}", LogLevel.NORMAL, "Effect")

        if extra_dice_count > 0:
            if self.computed_speed_dice:
                d_min, d_max = self.computed_speed_dice[0]
            else:
                d_min, d_max = self.base_speed_min, self.base_speed_max

            for _ in range(extra_dice_count):
                val = max(1, random.randint(d_min, d_max) + speed_modifier)
                self.active_slots.append({
                    'speed': val, 'card': None, 'target_slot': None,
                    'is_aggro': False, 'source_effect': 'Bonus 🌟'
                })
                speed_rolls.append(f"{val} (Bonus)")

        logger.log(f"{self.name} speed rolls: {speed_rolls} (Mod: {speed_modifier})", LogLevel.NORMAL, "Speed")

        # Хуки на модификацию слотов после создания
        for slot in self.active_slots:
            for effect in active_mechanics:
                if hasattr(effect, "modify_active_slot"):
                    effect.modify_active_slot(self, slot)