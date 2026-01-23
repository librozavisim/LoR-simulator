from typing import TYPE_CHECKING
from core.logging import logger, LogLevel
from logic.scripts.utils import _check_conditions, _resolve_value

if TYPE_CHECKING:
    from logic.context import RollContext


def modify_roll_power(ctx: 'RollContext', params: dict):
    if not _check_conditions(ctx.source, params): return
    amount = _resolve_value(ctx.source, ctx.target, params)
    if amount == 0: return

    reason = params.get("reason", "Bonus")
    if reason == "Bonus" and params.get("stat"):
        reason = f"{params['stat'].title()} scale"

    ctx.modify_power(amount, reason)
    logger.log(f"Modify Power: {amount} ({reason}) for {ctx.source.name}", LogLevel.VERBOSE, "Scripts")


def convert_status_to_power(ctx: 'RollContext', params: dict):
    status_id = params.get("status")
    factor = params.get("factor", 1.0)
    stack_count = ctx.source.get_status(status_id)
    if stack_count <= 0: return
    bonus = int(stack_count * factor)
    ctx.modify_power(bonus, f"Consumed {status_id.capitalize()}")
    ctx.source.remove_status(status_id, stack_count)
    logger.log(f"🔋 Converted {stack_count} {status_id} -> +{bonus} Power", LogLevel.VERBOSE, "Scripts")


def lima_ram_logic(ctx: 'RollContext', params: dict):
    unit = ctx.source
    haste = unit.get_status("haste")
    base_bonus = 0
    if haste >= 20:
        base_bonus = 5
    elif haste >= 14:
        base_bonus = 4
    elif haste >= 9:
        base_bonus = 3
    elif haste >= 5:
        base_bonus = 2
    elif haste >= 2:
        base_bonus = 1
    lvl_mult = int(unit.level / 3)
    final_bonus = base_bonus * lvl_mult
    if final_bonus > 0:
        ctx.modify_power(final_bonus, f"Ram (Haste {haste} * Lvl {unit.level}/3)")
    if haste > 0:
        unit.remove_status("haste", 999)
        if ctx.log: ctx.log.append(f"📉 **{unit.name}** consumed all Haste")
        logger.log(f"📉 Ram Logic: {final_bonus} Power, Haste Consumed", LogLevel.VERBOSE, "Scripts")