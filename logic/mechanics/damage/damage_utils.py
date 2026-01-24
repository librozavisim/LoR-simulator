from core.logging import logger, LogLevel

def _check_death_threshold(unit, current_val, max_val, resource_name):
    if current_val <= 0:
        overkill = abs(current_val)
        unit.overkill_damage = overkill
        return 0
    return current_val

def _get_attack_info(source_ctx):
    dtype_name = "slash"
    dice_obj = None
    if source_ctx and source_ctx.dice:
        dice_obj = source_ctx.dice
        dtype_name = dice_obj.dtype.value.lower()
    return dtype_name, dice_obj

def defender_name_safe(unit):
    return unit.name if hasattr(unit, 'name') else "Unknown"

def _apply_resource_damage(target, amount: int, resource_type: str, source_ctx, log_prefix=""):
    """Применяет финальный урон к ресурсам (HP/SP) и логирует результат."""
    if resource_type == "hp":
        new_val = target.current_hp - amount
        target.current_hp = _check_death_threshold(target, new_val, target.max_hp, "HP")

        hit_msg = f"💥 **{target.name}**: {log_prefix}Hit {amount} HP"
        if target.is_staggered():
            hit_msg += " (Staggered)"

        if target.current_hp == 0 and target.overkill_damage > 0:
            hit_msg += f" (DEAD! Overkill: {target.overkill_damage})"

        if source_ctx: source_ctx.log.append(hit_msg)
        logger.log(f"💥 {target.name} took {amount} HP Damage", LogLevel.MINIMAL, "Damage")

    elif resource_type == "sp":
        new_val = target.current_sp - amount
        target.current_sp = _check_death_threshold(target, new_val, target.max_sp, "SP")

        if source_ctx:
            source_ctx.log.append(f"🧠 **White Dmg**: {amount} SP")
            if target.current_sp == 0 and target.overkill_damage > 0:
                source_ctx.log.append(f"🤯 **PANIC/DEATH**: Overkill {target.overkill_damage}")

        logger.log(f"🧠 {defender_name_safe(target)} took {amount} SP Damage (White)", LogLevel.MINIMAL, "Damage")