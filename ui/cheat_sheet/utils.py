from core.game_templates import CHARACTER_TEMPLATES

def get_base_roll(lvl):
    if lvl >= 90: return 30, 40
    if lvl >= 80: return 25, 32
    if lvl >= 65: return 21, 27
    if lvl >= 50: return 17, 22
    if lvl >= 43: return 14, 19
    if lvl >= 36: return 11, 16
    if lvl >= 30: return 9, 13
    if lvl >= 24: return 7, 10
    if lvl >= 18: return 5, 7
    if lvl >= 12: return 4, 6
    if lvl >= 6:  return 3, 5
    return 1, 3

def get_base_rolls_data():
    """Возвращает список кортежей (level, rank_name, min, max)."""
    data = []
    for tmpl in CHARACTER_TEMPLATES:
        rmin, rmax = get_base_roll(tmpl['level'])
        data.append((tmpl['level'], tmpl['rank_name'], rmin, rmax))
    data.sort(key=lambda x: x[0])
    return data