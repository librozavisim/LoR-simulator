# core/unit/mixins/mechanics.py

class UnitMechanicsMixin:
    """
    Миксин, предоставляющий единый интерфейс для доступа ко всем
    источникам механик (Пассивки, Таланты, Аугментации, Статусы, Оружие).
    """

    def iter_mechanics(self):
        """
        Генератор, возвращающий все активные объекты эффектов на юните.
        Порядок: Статусы -> Пассивки -> Таланты -> Аугментации -> Оружие.
        """
        # Локальные импорты для предотвращения циклической зависимости
        from logic.character_changing.passives import PASSIVE_REGISTRY
        from logic.character_changing.talents import TALENT_REGISTRY
        from logic.character_changing.augmentations.augmentations import AUGMENTATION_REGISTRY
        from logic.statuses.status_manager import STATUS_REGISTRY
        from logic.weapon_definitions import WEAPON_REGISTRY

        # 1. Статусы (У них приоритет, т.к. они часто меняют логику статов)
        if hasattr(self, "statuses"):
            for status_id, stack in self.statuses.items():
                if status_id in STATUS_REGISTRY:
                    # Статусам часто нужен stack, но итератор возвращает сам объект.
                    # Логика обработки стаков должна быть внутри вызывающего кода
                    # или объект статуса должен быть stateless.
                    yield STATUS_REGISTRY[status_id]

        # 2. Пассивки
        if hasattr(self, "passives"):
            for pid in self.passives:
                if pid in PASSIVE_REGISTRY: yield PASSIVE_REGISTRY[pid]

        # 3. Таланты
        if hasattr(self, "talents"):
            for tid in self.talents:
                if tid in TALENT_REGISTRY: yield TALENT_REGISTRY[tid]

        # 4. Аугментации
        if hasattr(self, "augmentations"):
            for aid in self.augmentations:
                if aid in AUGMENTATION_REGISTRY: yield AUGMENTATION_REGISTRY[aid]

        # 5. Пассивка оружия
        if hasattr(self, "weapon_id") and self.weapon_id in WEAPON_REGISTRY:
            wep = WEAPON_REGISTRY[self.weapon_id]
            if wep.passive_id and wep.passive_id in PASSIVE_REGISTRY:
                yield PASSIVE_REGISTRY[wep.passive_id]

    def trigger_mechanics(self, method_name, *args, **kwargs):
        """
        Запускает метод method_name у всех механик, если он существует.
        Пример: unit.trigger_mechanics("on_combat_start", unit, log_func)
        """
        for mech in self.iter_mechanics():
            if hasattr(mech, method_name):
                getattr(mech, method_name)(*args, **kwargs)

    def apply_mechanics_filter(self, method_name, initial_value, *args, **kwargs):
        """
        Прогоняет значение через цепочку модификаторов.
        Пример: damage = unit.apply_mechanics_filter("modify_incoming_damage", damage, dmg_type)
        """
        value = initial_value
        for mech in self.iter_mechanics():
            if hasattr(mech, method_name):
                value = getattr(mech, method_name)(self, value, *args, **kwargs)
        return value