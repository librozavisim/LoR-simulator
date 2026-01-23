from core.logging import logger, LogLevel
from logic.calculations.base_calc import get_word, get_modded_value


def calculate_speed_dice(unit, speed_val, mods):
    """Считает кубики скорости с поддержкой оверкапа."""
    dice_count = speed_val // 10 + 1
    final_dice = []
    global_init = mods["initiative"]["flat"]

    for i in range(dice_count):
        points = max(0, min(10, speed_val - (i * 10)))
        skill_bonus = points // 2

        d_min = int(unit.base_speed_min + global_init + skill_bonus)
        d_max = int(unit.base_speed_max + global_init + skill_bonus)
        final_dice.append((d_min, d_max))

    unit.computed_speed_dice = final_dice
    unit.speed_dice_count = dice_count


def calculate_pools(unit, attrs, skills, mods):
    """
    Расчет HP, SP и Stagger.
    """
    # --- 1. HP ---
    base_h = unit.base_hp
    rolls_h = 0

    # Кастомная прогрессия
    custom_growth = False
    if hasattr(unit, "iter_mechanics"):
        for mech in unit.iter_mechanics():
            growth_data = mech.calculate_level_growth(unit)
            if growth_data:
                rolls_h = growth_data.get("hp", 0)
                if "logs" in growth_data:
                    for l in growth_data["logs"]: logger.log(l, LogLevel.VERBOSE, "Stats")
                custom_growth = True
                break

    if not custom_growth:
        rolls_h = sum(5 + v.get("hp", 0) for v in unit.level_rolls.values())

    endurance_val = attrs["endurance"]
    hp_flat_attr = 5 * (endurance_val // 3)
    hp_pct_attr = min(abs(endurance_val) * 2, 100)
    if endurance_val < 0: hp_pct_attr = -hp_pct_attr

    if endurance_val != 0:
        word = get_word(endurance_val)
        logger.log(f"{word} максимальный показатель ❤️ здоровья на {abs(hp_pct_attr)}% от основного", LogLevel.VERBOSE,
                   "Stats")

    if hp_flat_attr != 0:
        action = "получает дополнительные" if hp_flat_attr > 0 else "теряет"
        logger.log(f"Персонаж {action} {abs(hp_flat_attr)} ❤️ здоровья", LogLevel.VERBOSE, "Stats")

    mods["hp"]["flat"] += base_h + rolls_h + hp_flat_attr + unit.implants_hp_flat
    mods["hp"]["pct"] += hp_pct_attr + unit.implants_hp_pct + unit.talents_hp_pct
    unit.max_hp = get_modded_value(0, "hp", mods)

    # --- 2. SP ---
    base_s = unit.base_sp
    rolls_s = 0
    if not custom_growth:
        rolls_s = sum(5 + v.get("sp", 0) for v in unit.level_rolls.values())
    elif hasattr(unit, "iter_mechanics"):  # Если кастом, нужно перечитать SP
        for mech in unit.iter_mechanics():
            growth = mech.calculate_level_growth(unit)
            if growth: rolls_s = growth.get("sp", 0); break

    psych_val = attrs["psych"]
    sp_flat_attr = 5 * (psych_val // 3)
    sp_pct_attr = min(abs(psych_val) * 2, 100)
    if psych_val < 0: sp_pct_attr = -sp_pct_attr

    if psych_val != 0:
        word = get_word(psych_val)
        logger.log(f"{word} максимальный показатель 🧠 рассудка на {abs(sp_pct_attr)}% от основного", LogLevel.VERBOSE,
                   "Stats")

    if sp_flat_attr != 0:
        action = "получает дополнительные" if sp_flat_attr > 0 else "теряет"
        logger.log(f"Персонаж {action} {abs(sp_flat_attr)} 🧠 рассудка", LogLevel.VERBOSE, "Stats")

    mods["sp"]["flat"] += base_s + rolls_s + sp_flat_attr + unit.implants_sp_flat
    mods["sp"]["pct"] += sp_pct_attr + unit.implants_sp_pct + unit.talents_sp_pct
    unit.max_sp = get_modded_value(0, "sp", mods)

    # --- 3. Stagger ---
    base_stg = unit.max_hp // 2
    stg_pct = min(skills["willpower"], 50)

    if stg_pct != 0:
        word = get_word(stg_pct)
        logger.log(f"{word} 😵 выдержку на {abs(stg_pct)}%", LogLevel.VERBOSE, "Stats")

    mods["stagger"]["flat"] += base_stg + unit.implants_stagger_flat
    mods["stagger"]["pct"] += stg_pct + unit.implants_stagger_pct
    unit.max_stagger = get_modded_value(0, "stagger", mods)