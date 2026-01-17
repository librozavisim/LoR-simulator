import random
from core.enums import DiceType
from logic.character_changing.talents import TALENT_REGISTRY
from logic.context import RollContext
from logic.statuses.base_status import StatusEffect
from core.logging import logger, LogLevel


# === STANDARD STATUSES ===

class StrengthStatus(StatusEffect):
    id = "strength"

    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            ctx.modify_power(stack, "Strength")
            # logger.log(f"💪 Strength: +{stack} for {ctx.source.name}", LogLevel.VERBOSE, "Status")


class BindStatus(StatusEffect):
    id = "bind"
    pass


class EnduranceStatus(StatusEffect):
    id = "endurance"

    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype == DiceType.BLOCK or ctx.dice.dtype == DiceType.EVADE:
            ctx.modify_power(stack, "Endurance")
            # logger.log(f"🛡️ Endurance: +{stack} for {ctx.source.name}", LogLevel.VERBOSE, "Status")


class BleedStatus(StatusEffect):
    id = "bleed"

    def on_hit(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            dmg = stack

            if ctx.source.get_status("bleed_resist") > 0:
                # Снижаем на 33%
                dmg = int(dmg * 0.67)

            # Учет талантов (например, Survivor)
            if hasattr(ctx.source, "talents"):
                for talent_id in ctx.source.talents:
                    talent = TALENT_REGISTRY.get(talent_id)
                    if talent and hasattr(talent, "modify_incoming_damage"):
                        dmg = talent.modify_incoming_damage(ctx.source, dmg, "bleed")

            ctx.source.current_hp = max(0, ctx.source.current_hp - dmg)

            remove_amt = stack // 2
            ctx.source.remove_status("bleed", remove_amt)

            ctx.log.append(f"🩸 Bleed: {ctx.source.name} takes {dmg} dmg")
            logger.log(f"🩸 Bleed: {ctx.source.name} took {dmg} damage (Stack: {stack}->{stack - remove_amt})",
                       LogLevel.VERBOSE, "Status")


class ParalysisStatus(StatusEffect):
    id = "paralysis"

    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice:
            # Рассчитываем разницу между базовым броском и минимальным возможным
            diff = ctx.dice.min_val - ctx.base_value

            # Применяем штраф, только если он отрицательный (не даем бонусов)
            if diff < 0:
                ctx.modify_power(diff, "Paralysis (Min)")
                logger.log(f"⚡ Paralysis: {ctx.source.name} roll reduced by {abs(diff)}", LogLevel.VERBOSE, "Status")

            # Снимаем 1 стак
            ctx.source.remove_status("paralysis", 1)


class ProtectionStatus(StatusEffect):
    id = "protection"
    # Логика в damage.py
    pass


class FragileStatus(StatusEffect):
    id = "fragile"
    # Логика в damage.py
    pass


class VulnerabilityStatus(StatusEffect):
    id = "vulnerability"
    # Логика в damage.py
    pass


class BarrierStatus(StatusEffect):
    id = "barrier"
    # Логика в damage.py
    pass


class DeepWoundStatus(StatusEffect):
    id = "deep_wound"
    name = "Глубокая рана"
    description = (
        "При лечении: Тратится 1 заряд, лечение снижается до 75%.\n"
        "При использовании Защиты (Block/Evade): Получает урон = стакам, затем накладывается столько же Кровотечения."
    )

    def on_roll(self, ctx: RollContext, stack: int):
        # Проверяем, является ли кубик защитным
        if ctx.dice and ctx.dice.dtype in [DiceType.BLOCK, DiceType.EVADE]:
            dmg = stack

            # Allow mechanics to modify incoming burn damage (using 'burn' type as placeholder or create new)
            if hasattr(ctx.source, "apply_mechanics_filter"):
                dmg = ctx.source.apply_mechanics_filter("modify_incoming_damage", dmg, "deep_wound", stack=stack)

            # Apply damage to HP
            ctx.source.current_hp = max(0, ctx.source.current_hp - dmg)

            # Накладываем Кровотечение
            ctx.source.add_status("bleed", stack, duration=3)

            ctx.log.append(f"💔 **Глубокая рана**: Защита вскрыла раны! -{dmg} HP и +{stack} Bleed.")
            logger.log(f"💔 Deep Wound triggered on {ctx.source.name}: -{dmg} HP", LogLevel.NORMAL, "Status")

    def apply_heal_reduction(self, unit, amount: int) -> int:
        """
        Метод вызывается при попытке лечения.
        Возвращает уменьшенное значение лечения.
        """
        # Снижаем лечение до 75%
        new_amount = int(amount * 0.75)

        # Тратим 1 заряд
        unit.remove_status("deep_wound", 1)

        logger.log(f"💔 Deep Wound reduced healing on {unit.name}: {amount} -> {new_amount}", LogLevel.VERBOSE, "Status")
        return new_amount


class HasteStatus(StatusEffect):
    id = "haste"
    name = "Спешка"
    pass


class SlowStatus(StatusEffect):
    id = "slow"
    name = "Замедление"
    pass


class BurnStatus(StatusEffect):
    id = "burn"

    def on_round_end(self, unit, log_func, stack: int = 0, **kwargs):
        if stack <= 0:
            return []

        msgs = []
        dmg = stack

        # Allow mechanics to modify incoming burn damage
        if hasattr(unit, "apply_mechanics_filter"):
            dmg = unit.apply_mechanics_filter("modify_incoming_damage", dmg, "burn", stack=stack)

        # Apply damage to HP
        unit.current_hp = max(0, unit.current_hp - dmg)

        if log_func:
            log_func(f"🔥 Burn: {unit.name} takes {dmg} dmg")

        logger.log(f"🔥 Burn: {unit.name} took {dmg} damage", LogLevel.VERBOSE, "Status")

        msgs.append(f"🔥 Burn: -{dmg} HP")

        # Trigger on_take_damage hooks
        try:
            if hasattr(unit, "trigger_mechanics"):
                unit.trigger_mechanics("on_take_damage", unit, dmg, None, log_func=log_func)
        except Exception:
            pass

        # Halve the remaining stack
        new_stack = stack // 2
        remove_amt = stack - new_stack
        if remove_amt > 0:
            unit.remove_status("burn", remove_amt)
            msgs.append(f"🔥 Burn reduced: {stack} -> {new_stack}")

        return msgs