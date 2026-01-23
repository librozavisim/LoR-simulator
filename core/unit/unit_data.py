from dataclasses import dataclass

# Импортируем миксины из подпапок
from core.unit.data.base import UnitBaseMixin
from core.unit.data.rpg import UnitRPGMixin
from core.unit.data.combat import UnitCombatMixin
from core.unit.data.serialization import UnitSerializationMixin

# Порядок наследования важен для dataclasses (поля без дефолтных значений должны идти первыми)
# UnitBaseMixin содержит 'name' (без дефолта), поэтому он первый.
@dataclass
class UnitData(UnitBaseMixin, UnitCombatMixin, UnitRPGMixin, UnitSerializationMixin):
    """
    Сборный класс данных юнита.
    Наследует поля и методы из Mixin-классов для разделения ответственности.
    """
    pass