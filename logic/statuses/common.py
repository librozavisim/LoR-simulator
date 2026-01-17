from core.enums import DiceType
from core.logging import logger, LogLevel
from logic.character_changing.talents import TALENT_REGISTRY
from logic.context import RollContext
from logic.statuses.base_status import StatusEffect


# === STANDARD STATUSES ===

class StrengthStatus(StatusEffect):
    id = "strength"
    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            ctx.modify_power(stack, "Strength")

class BindStatus(StatusEffect):
    id = "bind"
    pass

class EnduranceStatus(StatusEffect):
    id = "endurance"
    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype == DiceType.BLOCK or ctx.dice.dtype == DiceType.EVADE:
            ctx.modify_power(stack, "Endurance")

class BleedStatus(StatusEffect):
    id = "bleed"

    def on_hit(self, ctx: RollContext, stack: int):
        if ctx.dice.dtype in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            dmg = stack

            if ctx.source.get_status("bleed_resist") > 0:
                dmg = int(dmg * 0.67)

            if hasattr(ctx.source, "talents"):
                for talent_id in ctx.source.talents:
                    talent = TALENT_REGISTRY.get(talent_id)
                    if talent and hasattr(talent, "modify_incoming_damage"):
                        dmg = talent.modify_incoming_damage(ctx.source, dmg, "bleed")

            ctx.source.current_hp = max(0, ctx.source.current_hp - dmg)

            remove_amt = stack // 2
            ctx.source.remove_status("bleed", remove_amt)

            ctx.log.append(f"🩸 Bleed: {ctx.source.name} takes {dmg} dmg")
            # [CHANGE] VERBOSE -> MINIMAL
            logger.log(f"🩸 Bleed: {ctx.source.name} took {dmg} damage (Stack: {stack}->{stack - remove_amt})",
                       LogLevel.MINIMAL, "Status")


class ParalysisStatus(StatusEffect):
    id = "paralysis"
    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice:
            diff = ctx.dice.min_val - ctx.base_value
            if diff < 0:
                ctx.modify_power(diff, "Paralysis (Min)")
                logger.log(f"⚡ Paralysis: {ctx.source.name} roll reduced by {abs(diff)}", LogLevel.VERBOSE, "Status")
            ctx.source.remove_status("paralysis", 1)

class ProtectionStatus(StatusEffect):
    id = "protection"
    pass

class FragileStatus(StatusEffect):
    id = "fragile"
    pass

class VulnerabilityStatus(StatusEffect):
    id = "vulnerability"
    pass

class BarrierStatus(StatusEffect):
    id = "barrier"
    pass

class DeepWoundStatus(StatusEffect):
    id = "deep_wound"
    name = "Глубокая рана"
    description = (
        "При лечении: Тратится 1 заряд, лечение снижается до 75%.\n"
        "При использовании Защиты (Block/Evade): Получает урон = стакам, затем накладывается столько же Кровотечения."
    )

    def on_roll(self, ctx: RollContext, stack: int):
        if ctx.dice and ctx.dice.dtype in [DiceType.BLOCK, DiceType.EVADE]:
            dmg = stack
            if hasattr(ctx.source, "apply_mechanics_filter"):
                dmg = ctx.source.apply_mechanics_filter("modify_incoming_damage", dmg, "deep_wound", stack=stack)

            ctx.source.current_hp = max(0, ctx.source.current_hp - dmg)
            ctx.source.add_status("bleed", stack, duration=3)

            ctx.log.append(f"💔 **Глубокая рана**: Защита вскрыла раны! -{dmg} HP и +{stack} Bleed.")
            # [CHANGE] NORMAL -> MINIMAL
            logger.log(f"💔 Deep Wound triggered on {ctx.source.name}: -{dmg} HP", LogLevel.MINIMAL, "Status")

    def apply_heal_reduction(self, unit, amount: int) -> int:
        new_amount = int(amount * 0.75)
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

        if hasattr(unit, "apply_mechanics_filter"):
            dmg = unit.apply_mechanics_filter("modify_incoming_damage", dmg, "burn", stack=stack)

        unit.current_hp = max(0, unit.current_hp - dmg)

        if log_func:
            log_func(f"🔥 Burn: {unit.name} takes {dmg} dmg")

        # [CHANGE] VERBOSE -> MINIMAL
        logger.log(f"🔥 Burn: {unit.name} took {dmg} damage", LogLevel.MINIMAL, "Status")

        msgs.append(f"🔥 Burn: -{dmg} HP")

        try:
            if hasattr(unit, "trigger_mechanics"):
                unit.trigger_mechanics("on_take_damage", unit, dmg, None, log_func=log_func)
        except Exception:
            pass

        new_stack = stack // 2
        remove_amt = stack - new_stack
        if remove_amt > 0:
            unit.remove_status("burn", remove_amt)
            msgs.append(f"🔥 Burn reduced: {stack} -> {new_stack}")

        return msgs