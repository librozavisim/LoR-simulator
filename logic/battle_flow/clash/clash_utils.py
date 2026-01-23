from core.enums import DiceType
from core.logging import logger, LogLevel


def check_destruction_immunity(unit):
    """Проверяет, есть ли у юнита иммунитет к разрушению кубиков скоростью."""
    if hasattr(unit, "iter_mechanics"):
        for mech in unit.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(unit):
                return True
    return False


def resolve_slot_die(unit, queue, idx, is_broken, active_counter_tuple):
    """
    Определяет, какой кубик будет использоваться:
    1. Активный контр-кубик (если есть).
    2. Кубик из очереди (если не сломан).
    3. Stored/Counter кубик (если слот пуст/сломан).

    Возвращает: (dice_obj, is_counter_source)
    """
    if active_counter_tuple:
        return active_counter_tuple[0], active_counter_tuple[1]

    card_die = None
    if idx < len(queue):
        card_die = queue[idx]
        if is_broken:
            is_saved = False
            if hasattr(unit, "iter_mechanics"):
                for mech in unit.iter_mechanics():
                    if mech.prevents_specific_die_destruction(unit, card_die):
                        is_saved = True
                        break
            if not is_saved:
                card_die = None
            else:
                logger.log(f"{unit.name}: Die #{idx + 1} saved from destruction", LogLevel.VERBOSE, "Clash")

    if not card_die:
        # Попытка использовать Stored Dice
        if hasattr(unit, 'stored_dice') and isinstance(unit.stored_dice, list) and unit.stored_dice:
            if unit.is_staggered():
                can_use = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.can_use_counter_die_while_staggered(unit):
                            can_use = True
                            break
                if not can_use: return None, False
            logger.log(f"{unit.name}: Using Stored Dice", LogLevel.VERBOSE, "Clash")
            return unit.stored_dice.pop(0), True

        # Попытка использовать Counter Dice (из пассивок/защиты)
        if unit.counter_dice:
            if unit.is_staggered():
                can_use = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.can_use_counter_die_while_staggered(unit):
                            can_use = True
                            break
                if not can_use: return None, False
            logger.log(f"{unit.name}: Using Counter Dice", LogLevel.VERBOSE, "Clash")
            return unit.counter_dice.pop(0), True

        return None, False

    return card_die, False


def store_remaining_dice(unit, queue, idx, active_cnt_tuple, log_list):
    """Сохраняет неиспользованные кубики уклонения."""
    if not hasattr(unit, 'stored_dice') or not isinstance(unit.stored_dice, list):
        unit.stored_dice = []

    # Если остался активный контр-кубик (ресайкнутый)
    if active_cnt_tuple:
        die, is_from_storage = active_cnt_tuple
        if die.dtype == DiceType.EVADE:
            if is_from_storage:
                unit.stored_dice.append(die)
                logger.log(f"{unit.name} kept counter evade", LogLevel.NORMAL, "Clash")
                log_list.append({"type": "info", "outcome": f"🛡️ {unit.name} Kept Counter Evade", "details": []})

    # Проходим по оставшейся очереди
    while idx < len(queue):
        die = queue[idx]
        if die.dtype == DiceType.EVADE:
            unit.stored_dice.append(die)
            logger.log(f"{unit.name} stored unused evade", LogLevel.NORMAL, "Clash")
            log_list.append({
                "type": "info",
                "outcome": f"🛡️ {unit.name} Stored Evade Die",
                "details": [f"Die {die.min_val}-{die.max_val} saved."]
            })
        idx += 1