import copy
from typing import TYPE_CHECKING

from core.logging import logger, LogLevel
from logic.scripts.utils import _check_conditions

if TYPE_CHECKING:
    from logic.context import RollContext

def add_luck_bonus_roll(ctx: 'RollContext', params: dict):
    """Добавляет бонус к броску на основе Удачи (Luck)."""
    if not _check_conditions(ctx.source, params): return
    step = int(params.get("step", 10))
    limit = int(params.get("limit", 999))

    # Берем удачу из ресурсов
    luck = ctx.source.resources.get("luck", 0)

    if step <= 0: step = 1
    bonus = luck // step
    bonus = min(bonus, limit)

    if bonus > 0:
        ctx.modify_power(bonus, f"Luck ({luck})")
        logger.log(f"🍀 Luck Bonus: +{bonus} (Luck: {luck})", LogLevel.VERBOSE, "Scripts")

def scale_roll_by_luck(ctx: 'RollContext', params: dict):
    """
    Серия ударов: Бросок повторяется за каждые X удачи.
    Реализация: Увеличивает итоговое значение броска (множитель).
    """
    step = int(params.get("step", 10))  # Каждые 10 удачи
    limit = int(params.get("limit", 7))  # Лимит повторов

    luck = ctx.source.resources.get("luck", 0)

    if step <= 0: step = 1

    # Считаем множитель
    repeats = luck // step
    repeats = min(repeats, limit)

    if repeats > 0:
        base_val = ctx.final_value
        bonus = base_val * repeats
        ctx.modify_power(bonus, f"Luck x{repeats}")
        logger.log(f"🍀 Luck Scaling: x{repeats} (Total: +{bonus})", LogLevel.VERBOSE, "Scripts")

def add_power_by_luck(ctx: 'RollContext', params: dict):
    """
    Удар фортуны: Каждые X удачи добавляют 1 к силе.
    """
    step = int(params.get("step", 5))  # Каждые 5 удачи
    limit = int(params.get("limit", 15))  # Лимит

    luck = ctx.source.resources.get("luck", 0)

    if step <= 0: step = 1

    bonus = luck // step
    bonus = min(bonus, limit)

    if bonus > 0:
        ctx.modify_power(bonus, f"Fortune ({bonus})")
        logger.log(f"🍀 Fortune Power: +{bonus}", LogLevel.VERBOSE, "Scripts")


def repeat_dice_by_luck(ctx: 'RollContext', params: dict):
    """
    Добавляет копии кубиков в карту в зависимости от Удачи.
    Работает на триггере 'on_use'.
    """
    step = int(params.get("step", 10))  # Каждые 10 удачи
    limit = int(params.get("limit", 10))  # Максимум 10 доп. ударов

    luck = ctx.source.resources.get("luck", 0)

    if step <= 0: step = 1
    repeats = luck // step
    repeats = min(repeats, limit)

    if repeats <= 0:
        return

    card = ctx.source.current_card
    if not card or not card.dice_list:
        return

    # Берем первый кубик как шаблон
    template_die = card.dice_list[0]

    # Добавляем копии
    for _ in range(repeats):
        new_die = copy.deepcopy(template_die)
        card.dice_list.append(new_die)

    # Логируем и в UI, и в системный лог
    ctx.log.append(f"🍀 **Серия ударов**: Удача {luck} дала +{repeats} доп. кубиков!")
    logger.log(f"🍀 Luck Series: Added {repeats} dice to card {card.name}", LogLevel.NORMAL, "Scripts")