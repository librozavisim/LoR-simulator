from collections import defaultdict

def init_modifiers():
    """
    Создает динамическое хранилище модификаторов.
    Структура: { "stat_name": { "flat": 0.0, "pct": 0.0 } }
    """
    return defaultdict(lambda: {"flat": 0.0, "pct": 0.0})


def init_bonuses(unit):
    """
    Собирает временные бонусы к базовым атрибутам.
    """
    return defaultdict(int)