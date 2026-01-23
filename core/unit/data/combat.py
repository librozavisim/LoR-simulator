from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any

# Импорт Card с защитой от циклических ссылок
try:
    from core.card import Card
except ImportError:
    Card = Any


@dataclass
class UnitCombatMixin:
    """
    Динамическое состояние боя: HP, Стычки, Колода, Статусы.
    """
    # === РЕСУРСЫ (DYNAMIC) ===
    max_hp: int = 20
    current_hp: int = 20
    max_sp: int = 20
    current_sp: int = 20
    max_stagger: int = 10
    current_stagger: int = 10

    # === КОЛОДА И КУЛДАУНЫ ===
    deck: List[str] = field(default_factory=list)
    card_cooldowns: Dict[str, int] = field(default_factory=dict)
    cooldowns: Dict[str, int] = field(default_factory=dict)  # Способности

    # === БОЕВОЕ ПОЛЕ ===
    computed_speed_dice: List[Tuple[int, int]] = field(default_factory=list)
    active_slots: List[Dict] = field(default_factory=list)
    current_card: Optional[Card] = None
    stored_dice: List = field(default_factory=list)
    counter_dice: List = field(default_factory=list)

    # === СОСТОЯНИЯ ===
    active_buffs: Dict[str, int] = field(default_factory=dict)
    _status_effects: Dict[str, List[Dict]] = field(default_factory=dict)
    delayed_queue: List[dict] = field(default_factory=list)

    # Временные модификаторы боя
    modifiers: Dict[str, int] = field(default_factory=dict)

    # Доп. ресурсы (патроны, заряд и т.д.)
    resources: Dict[str, int] = field(default_factory=dict)

    # Память для скриптов
    memory: Dict[str, Any] = field(default_factory=dict)

    # Статистика боя
    death_count: int = 0
    overkill_damage: int = 0