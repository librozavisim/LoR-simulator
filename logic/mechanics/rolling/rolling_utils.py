import random

def safe_randint(min_val: int, max_val: int) -> int:
    """
    Безопасный рандом: если min > max, меняет их местами.
    """
    if min_val > max_val:
        return random.randint(max_val, min_val)
    return random.randint(min_val, max_val)