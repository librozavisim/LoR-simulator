from core.logging import logger, LogLevel
from logic.calculations.base_calc import get_word, safe_int_div

def apply_attribute_effects(attrs, mods):
    """
    Применяет эффекты от атрибутов к модификаторам.
    """
    # --- СИЛА ---
    sila = attrs["strength"]
    mod_sila = safe_int_div(sila, 3)
    mod_sila_5 = safe_int_div(sila, 5)

    if mod_sila != 0:
        word = get_word(mod_sila)
        logger.log(f"{word} значение броска силы на {abs(mod_sila)}", LogLevel.VERBOSE, "Stats")

    if mod_sila_5 != 0:
        word = get_word(mod_sila_5)
        mods["power_attack"]["flat"] += mod_sila_5
        logger.log(f"{word} значение куба ⚔️ атаки на {abs(mod_sila_5)}", LogLevel.VERBOSE, "Stats")

    # --- СТОЙКОСТЬ ---
    stoyk = attrs["endurance"]
    mod_stoyk_5 = safe_int_div(stoyk, 5)

    if mod_stoyk_5 != 0:
        word = get_word(mod_stoyk_5)
        mods["power_block"]["flat"] += mod_stoyk_5
        logger.log(f"{word} значение куба 🛡️ блока на {abs(mod_stoyk_5)}", LogLevel.VERBOSE, "Stats")

    # --- ЛОВКОСТЬ ---
    lovkost = attrs["agility"]
    mod_lov = safe_int_div(lovkost, 3)
    mod_lov_5 = safe_int_div(lovkost, 5)

    if mod_lov != 0:
        word = get_word(mod_lov)
        mods["initiative"]["flat"] += mod_lov
        logger.log(f"{word} значение броска ловкости и 👢 инициативу на {abs(mod_lov)}", LogLevel.VERBOSE, "Stats")

    if mod_lov_5 != 0:
        word = get_word(mod_lov_5)
        mods["power_evade"]["flat"] += mod_lov_5
        logger.log(f"{word} значение куба 💨 уклонения на {abs(mod_lov_5)}", LogLevel.VERBOSE, "Stats")

    # --- МУДРОСТЬ ---
    mudrost = attrs["wisdom"]
    if abs(mudrost) >= 3:
        word = "Повышает" if mudrost > 0 else "Понижает"
        logger.log(f'{word} "интеллект" персонажа на основе его опыта', LogLevel.VERBOSE, "Stats")

    # --- ПСИХИКА ---
    psy = attrs["psych"]
    mod_psy = safe_int_div(psy, 3)
    if mod_psy != 0:
        word = get_word(mod_psy)
        logger.log(f"{word} значение бросков против необъяснимого на {abs(mod_psy)}", LogLevel.VERBOSE, "Stats")