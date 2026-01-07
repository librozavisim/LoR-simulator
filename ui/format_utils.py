# ui/format_utils.py

def format_large_number(value) -> str:
    """
    Форматирует большие числа с суффиксами к/М/Б.
    Округляет ВНИЗ (floor), чтобы не завышать значения.
    Пример: 1500 -> 1к, 99 999 999 -> 99М.
    """
    try:
        val = int(value)
    except (ValueError, TypeError):
        return str(value)

    # Меньше тысячи - показываем как есть
    if val < 1_000:
        return str(val)

    # Тысячи (к)
    if val < 1_000_000:
        return f"{int(val / 1_000)}к"

    # Миллионы (М) - используем "М" или "кк" по вкусу, но "М" профессиональнее
    # Если нужно "кк", замените "М" на "кк" ниже.
    if val < 1_000_000_000:
        return f"{int(val / 1_000_000)}М"

    # Миллиарды (Б)
    return f"{int(val / 1_000_000_000)}Б"