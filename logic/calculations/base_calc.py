def get_word(value, positive="Повышает", negative="Понижает"):
    return positive if value >= 0 else negative

def safe_int_div(val, div):
    """
    Деление с отбрасыванием дробной части через int(),
    чтобы -4 / 3 давало -1 (как в ТЗ), а не -2 (как // в Python).
    """
    return int(val / div)

def get_modded_value(base_val, stat_name, mods):
    """
    Универсальная формула: (Base + Flat) * (1 + Pct / 100)
    Округляет результат до целого.
    """
    flat = mods[stat_name]["flat"]
    pct = mods[stat_name]["pct"]

    total = (base_val + flat) * (1 + pct / 100.0)
    return int(total)