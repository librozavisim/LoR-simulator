from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from core.dice import Dice
from core.unit.unit import Unit
from core.enums import DiceType
from core.logging import logger, LogLevel


@dataclass
class RollContext:
    # ... (поля класса без изменений) ...
    source: 'Unit'
    target: Optional['Unit']
    dice: Optional['Dice']
    final_value: int = 0
    base_value: int = 0
    convert_hp_to_sp: bool = False
    opponent_ctx: Optional['RollContext'] = None
    log: List[str] = field(default_factory=list)
    modifiers_list: List[Tuple[int, str]] = field(default_factory=list)
    damage_multiplier: float = 1.0
    is_critical: bool = False
    is_disadvantage: bool = False

    def roll(self, stack=0):
        if self.dice:
            self.base_value = self.dice.roll()
            self.final_value = self.base_value

        self.calculate_power(stack)
        self._trigger_on_roll(stack)

        if self.final_value < 0: self.final_value = 0
        return self.final_value

    def calculate_power(self, stack=0):
        if not self.dice: return

        # 1. Проверка отключения кубиков (Block/Evade Disabled)
        disable_block = self.source.modifiers.get("disable_block", {}).get("flat", 0) > 0
        disable_evade = self.source.modifiers.get("disable_evade", {}).get("flat", 0) > 0

        if self.dice.dtype == DiceType.BLOCK and disable_block:
            self.modify_power(-9999, "Block Disabled 🚫")
            return
        if self.dice.dtype == DiceType.EVADE and disable_evade:
            self.modify_power(-9999, "Evade Disabled 🚫")
            return

        # === 2. ОПРЕДЕЛЕНИЕ БАЗОВОГО СТАТА ===
        base_stat_val = 0
        reason = "Stat"

        # Определяем стандартный стат (Сила, Стойкость, Акробатика)
        if self.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            base_stat_val = self.source.attributes.get("strength", 0)
            reason = "Strength"
        elif self.dice.dtype == DiceType.BLOCK:
            base_stat_val = self.source.attributes.get("endurance", 0)
            reason = "Endurance"
        elif self.dice.dtype == DiceType.EVADE:
            base_stat_val = self.source.skills.get("acrobatics", 0)
            reason = "Acrobatics"

        # [ХУК] Подмена стата (PassiveSourceAccess)
        if hasattr(self.source, "apply_mechanics_filter"):
            # Передаем (значение, имя), получаем (новое_значение, новое_имя)
            base_stat_val, reason = self.source.apply_mechanics_filter(
                "override_roll_base_stat",
                (base_stat_val, reason),
                dice=self.dice
            )

        # Применяем (базовый или подмененный) стат
        if base_stat_val != 0:
            self.modify_power(base_stat_val, reason)

        # === 3. МОДИФИКАТОРЫ (Buffs, Items) ===
        # Они добавляются ПОВЕРХ базы
        if self.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            mod_atk = self.source.modifiers.get("power_attack", {}).get("flat", 0)
            if mod_atk: self.modify_power(mod_atk, "Power Attack")

        elif self.dice.dtype == DiceType.BLOCK:
            mod_blk = self.source.modifiers.get("power_block", {}).get("flat", 0)
            if mod_blk: self.modify_power(mod_blk, "Power Block")

        elif self.dice.dtype == DiceType.EVADE:
            mod_evd = self.source.modifiers.get("power_evade", {}).get("flat", 0)
            if mod_evd: self.modify_power(mod_evd, "Power Evade")

        # Глобальный бонус
        power_all = self.source.modifiers.get("power_all", {}).get("flat", 0)
        if power_all != 0:
            self.modify_power(power_all, "Power All")

    def _trigger_on_roll(self, stack):
        all_ability_ids = self.source.passives + self.source.talents
        from logic.character_changing.passives import PASSIVE_REGISTRY
        from logic.character_changing.talents import TALENT_REGISTRY

        for pid in all_ability_ids:
            obj = PASSIVE_REGISTRY.get(pid) or TALENT_REGISTRY.get(pid)
            if obj and hasattr(obj, "on_roll"):
                obj.on_roll(self, stack=stack)

        from logic.statuses.status_manager import STATUS_REGISTRY
        for status_id, amount in self.source.statuses.items():
            if amount > 0 and status_id in STATUS_REGISTRY:
                st_obj = STATUS_REGISTRY[status_id]
                if hasattr(st_obj, "on_roll"):
                    st_obj.on_roll(self, stack=stack)

    def modify_power(self, amount: int, reason: str):
        if amount == 0: return
        self.final_value += amount
        self.modifiers_list.append((amount, reason))

    def get_formatted_roll_log(self) -> str:
        if not self.dice: return f"Value: {self.final_value}"
        parts = [str(self.base_value)]
        for amount, reason in self.modifiers_list:
            sign = "+" if amount >= 0 else "-"
            parts.append(f"{sign} {abs(amount)} ({reason})")
        formula = " ".join(parts)
        range_info = f"[{self.dice.min_val}-{self.dice.max_val}]"
        return f"🎲 Roll {range_info}: {formula} = **{self.final_value}**"