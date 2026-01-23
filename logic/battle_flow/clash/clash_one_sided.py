from core.enums import DiceType
from core.logging import logger, LogLevel


def manual_save_die(unit, die, detail_logs):
    """Принудительное сохранение кубика (Evade при отсутствии атаки)."""
    if not hasattr(unit, 'stored_dice') or not isinstance(unit.stored_dice, list):
        unit.stored_dice = []
    unit.stored_dice.append(die)

    msg = f"🛡️ {unit.name} Stored Evade (Auto)"
    if detail_logs is not None:
        detail_logs.append(msg)
    logger.log(f"{unit.name} stored evade die (auto-save)", LogLevel.NORMAL, "Clash")


def handle_one_sided_exchange(engine, active_side, passive_side, detail_logs):
    """
    Обрабатывает ситуацию, когда у active_side ЕСТЬ кубик, а у passive_side НЕТ.
    Возвращает outcome string.
    """
    die = active_side.current_die
    dtype = die.dtype

    # 1. Если активный кубик - Уклонение
    if dtype == DiceType.EVADE:
        manual_save_die(active_side.unit, die, detail_logs)
        # Уклонение сохраняется, но мы продвигаем индекс у "пустого" оппонента (если бы он был)
        passive_side.consume()  # Формально продвигаем, хотя там пусто
        active_side.consume()  # Убираем из активного слота (ушло в stored)
        return "🏃 Evade Saved (Opponent Broken)"

    # 2. Если активный кубик - Блок
    elif dtype == DiceType.BLOCK:
        active_side.consume()
        passive_side.consume()
        return "🛡️ Block Skipped (Opponent Broken)"

    # 3. Атака (Slash/Pierce/Blunt)
    else:
        outcome = f"🚫 {passive_side.unit.name} Broken"
        # Наносим урон, используя контекст активного
        if active_side.current_ctx:
            # apply_damage требует context атакующего и context защищающегося (или None)
            engine._apply_damage(active_side.current_ctx, None, "hp")

        active_side.consume()
        passive_side.consume()
        return outcome