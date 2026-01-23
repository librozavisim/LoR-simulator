from core.unit.mixins.mechanics import MechanicsIteratorMixin
from core.unit.mixins.speed import SpeedRollMixin
from core.unit.mixins.checks import StatusCheckMixin
from core.unit.mixins.cooldowns import CooldownsMixin

class UnitCombatMixin(MechanicsIteratorMixin, SpeedRollMixin, StatusCheckMixin, CooldownsMixin):
    """
    Сборный класс для боевой логики.
    Наследует функционал из специализированных миксинов.
    """
    pass