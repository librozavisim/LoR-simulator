from core.logging import logger, LogLevel
from logic.calculations.base_calc import get_word, safe_int_div

def apply_skill_effects(skills, mods):
    """
    Применяет эффекты от навыков к модификаторам.
    """
    # --- СИЛА УДАРА ---
    su = skills["strike_power"]
    mod_su = safe_int_div(su, 3)
    if mod_su != 0:
        word = get_word(mod_su)
        mods["damage_deal"]["flat"] += mod_su
        logger.log(f"Ваш показатель 💥 урона при ударе {word.lower()}ся на {abs(mod_su)}", LogLevel.VERBOSE, "Stats")

    # --- МЕДИЦИНА ---
    med = skills["medicine"]
    mod_med = safe_int_div(med, 3)
    if mod_med != 0:
        heal_eff = mod_med * 10
        word = get_word(mod_med, "повышается", "понижается")
        mods["heal_efficiency"]["pct"] += heal_eff
        logger.log(f"Ваш бросок 💚 медицины {word} на {abs(mod_med)}, эффективность лечения — {abs(heal_eff)}%", LogLevel.VERBOSE, "Stats")

    # --- АКРОБАТИКА ---
    acro = skills["acrobatics"]
    mod_acro = safe_int_div(acro, 3)
    if mod_acro != 0:
        val = int(mod_acro * 0.8)
        if val != 0:
            word = get_word(val)
            mods["power_evade"]["flat"] += val
            logger.log(f"{word} значение куба 💨 уклонения на {abs(val)} (Акробатика)", LogLevel.VERBOSE, "Stats")

    # --- ЩИТЫ ---
    shields = skills["shields"]
    mod_shields = safe_int_div(shields, 3)
    if mod_shields != 0:
        val = int(mod_shields * 0.8)
        if val != 0:
            word = get_word(val)
            mods["power_block"]["flat"] += val
            logger.log(f"{word} значение куба 🛡️ щита на {abs(val)}", LogLevel.VERBOSE, "Stats")

    # --- ОРУЖИЕ ---
    weapon_map = {
        "light_weapon": ("power_light", "лёгкого оружия"),
        "medium_weapon": ("power_medium", "среднего оружия"),
        "heavy_weapon": ("power_heavy", "тяжёлого оружия"),
        "firearms": ("power_ranged", "огнестрельного оружия")
    }

    for key, (mod_key, name_ru) in weapon_map.items():
        val = skills[key]
        mod_w = safe_int_div(val, 3)
        if mod_w != 0:
            word = get_word(mod_w)
            mods[mod_key]["flat"] += mod_w
            logger.log(f"{word} значение куба ⚔️ удара атакующими картами {name_ru} на {abs(mod_w)}", LogLevel.VERBOSE, "Stats")

    # --- КРЕПКАЯ КОЖА ---
    skin = skills["tough_skin"]
    mod_skin = safe_int_div(skin, 3)
    if mod_skin != 0:
        val = int(mod_skin * 1.2)
        if val > 0:
            mods["damage_take"]["flat"] += val
            logger.log(f"Понижает 🧱 получаемый урон на {val}", LogLevel.VERBOSE, "Stats")
        elif val < 0:
            mods["damage_take"]["flat"] += val
            logger.log(f"Повышает 🧱 получаемый урон на {abs(val)}", LogLevel.VERBOSE, "Stats")

    # --- СОЦИАЛЬНЫЕ И КРАФТ ---
    simple_skills = [
        ("eloquence", "значение броска при убеждении/торговле"),
        ("forging", "бросок качества создаваемого предмета"),
        ("engineering", "качество предметов и бросок инженерии"),
        ("programming", "успешность взлома и контроля механизмов")
    ]
    for key, desc in simple_skills:
        val = skills[key]
        if val != 0:
            word = get_word(val)
            logger.log(f"{word} {desc} на {abs(val)}", LogLevel.VERBOSE, "Stats")