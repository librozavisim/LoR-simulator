# === ОПРЕДЕЛЕНИЕ ГРУПП И НАЗВАНИЙ ===

TYPE_10_ATTRS = {
    "strength": "Сила", "agility": "Ловкость", "endurance": "Стойкость",
    "psych": "Психический порог", "willpower": "Сила воли"
}

TYPE_15_SKILLS = {
    "speed": "Скорость", "medicine": "Медицина",
    "strike_power": "Сила удара", "acrobatics": "Акробатика", "shields": "Щиты",
    "light_weapon": "Легкое оружие", "medium_weapon": "Среднее оружие", "heavy_weapon": "Тяжелое оружие",
    "firearms": "Огнестрельное оружие", "tough_skin": "Крепкая кожа", "eloquence": "Красноречие",
    "forging": "Ковка", "programming": "Программирование", "engineering": "Инженерия"
}

TYPE_WISDOM = {"wisdom": "Мудрость"}
TYPE_LUCK = {"luck": "Удача"}
TYPE_INTELLECT = {"intellect": "Интеллект"}

ALL_LABELS = {**TYPE_10_ATTRS, **TYPE_15_SKILLS, **TYPE_WISDOM, **TYPE_LUCK, **TYPE_INTELLECT}