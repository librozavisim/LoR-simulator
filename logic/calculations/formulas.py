def calculate_totals(unit, bonuses, mods):
    """Суммирует базу и бонусы, заполняет mods['total_X']."""
    attrs = {}
    for k in unit.attributes:
        val = unit.attributes[k] + bonuses[k]
        attrs[k] = val
        mods[k]["flat"] = val

    skills = {}
    for k in unit.skills:
        val = unit.skills[k] + bonuses[k]
        skills[k] = val
        mods[k]["flat"] = val

    base_int = unit.base_intellect + bonuses["bonus_intellect"] + (attrs["wisdom"] // 3)
    mods["total_intellect"]["flat"] = base_int
    mods["intellect"]["flat"] = base_int

    return attrs, skills

def finalize_state(unit, mods):
    """Финальные проверки."""
    unit.current_hp = min(unit.current_hp, unit.max_hp)
    unit.current_sp = min(unit.current_sp, unit.max_sp)
    unit.current_stagger = min(unit.current_stagger, unit.max_stagger)