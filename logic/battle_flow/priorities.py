from core.logging import logger, LogLevel


def get_action_priority(card):
    """
    Возвращает базовый приоритет действия на основе типа карты.
    Чем выше число, тем раньше сработает карта.
    """
    if not card: return 0

    ctype = str(card.card_type).lower()
    prio = 0

    # 1. Мгновенные эффекты
    if ctype == "on_play" or ctype == "on play":
        prio = 5000

    # 2. Массовые атаки (срабатывают до обычных столкновений)
    elif "mass" in ctype:
        prio = 4000

    # 3. Стрелковые (бьют первыми в фазе боя)
    elif ctype == "ranged":
        prio = 3000

    # 4. Наступательные (бьют перед обычными, но могут быть перехвачены)
    elif ctype == "offensive":
        prio = 2000

    # 5. Обычные (Рукопашные)
    elif ctype == "melee":
        prio = 1000

    # Логируем расчет приоритета (только для отладки порядка ходов)
    # logger.log(f"Priority calc: '{card.name}' ({ctype}) -> {prio}", LogLevel.VERBOSE, "Priority")

    return prio