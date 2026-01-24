from core.logging import logger, LogLevel


def fetch_next_counter(unit):
    """
    Ищет доступный контр-кубик (Stored или Counter) с учетом оглушения.
    """
    # 1. Stored Dice
    if hasattr(unit, 'stored_dice') and isinstance(unit.stored_dice, list) and unit.stored_dice:
        if unit.is_staggered():
            if not _can_use_while_staggered(unit): return None
        logger.log(f"{unit.name} retrieves Stored Die", LogLevel.VERBOSE, "OneSided")
        return unit.stored_dice.pop(0)

    # 2. Counter Dice
    if unit.counter_dice:
        if unit.is_staggered():
            if not _can_use_while_staggered(unit): return None
        logger.log(f"{unit.name} retrieves Counter Die", LogLevel.VERBOSE, "OneSided")
        return unit.counter_dice.pop(0)

    return None


def store_unused_counter(unit, active_counter_die):
    """Возвращает неиспользованный контр-кубик обратно в стек."""
    if active_counter_die:
        if not hasattr(unit, 'stored_dice') or not isinstance(unit.stored_dice, list):
            unit.stored_dice = []
        unit.stored_dice.insert(0, active_counter_die)
        logger.log(f"{unit.name} keeps unused counter die", LogLevel.VERBOSE, "OneSided")


def _can_use_while_staggered(unit):
    if hasattr(unit, "iter_mechanics"):
        for mech in unit.iter_mechanics():
            if mech.can_use_counter_die_while_staggered(unit):
                return True
    return False