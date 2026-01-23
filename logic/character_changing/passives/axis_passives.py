from logic.character_changing.passives.base_passive import BasePassive
from core.logging import logger, LogLevel
from logic.context import RollContext


class PassiveAxisUnity(BasePassive):
    id = "axis_unity"
    name = "Единство Тела, Души и Разума"
    description = (
        "Пока Аксис на поле боя:\n"
        "- Если на персонаже есть Сила, Стойкость и Спешка (мин 1): +1 ко всем этим эффектам.\n"
        "- Если на персонаже есть Слабость, Паралич и Замедление (мин 1): +1 ко всем этим эффектам.\n"
        "Бонус дается 1 раз за 'сборку' комбинации. Статусы обновляются мгновенно."
    )
    is_active_ability = False

    def _get_max_duration(self, unit, status_id):
        if not hasattr(unit, '_status_effects'): return 0
        effects = unit._status_effects.get(status_id, [])
        if not effects: return 0
        return max((eff.get('duration', 0) for eff in effects), default=0)

    def _evaluate_triad(self, target):
        """Проверяет статусы цели и активирует триаду."""
        if not target: return

        # === 1. ПОЛОЖИТЕЛЬНАЯ ТРИАДА (Strength, Endurance, Haste) ===
        has_str = target.get_status("strength") >= 1
        has_end = target.get_status("endurance") >= 1
        has_haste = target.get_status("haste") >= 1

        is_active = target.memory.get("axis_buff_triad_active", False)

        if has_str and has_end and has_haste:
            if not is_active:
                # Активация!
                d_str = self._get_max_duration(target, "strength")
                d_end = self._get_max_duration(target, "endurance")
                d_has = self._get_max_duration(target, "haste")

                target.add_status("strength", 1, duration=d_str, trigger_events=False)
                target.add_status("endurance", 1, duration=d_end, trigger_events=False)
                target.add_status("haste", 1, duration=d_has, trigger_events=False)

                target.memory["axis_buff_triad_active"] = True
                logger.log(f"✨ Axis Unity: Buff Triad activated on {target.name}", LogLevel.NORMAL, "Passive")
        else:
            # Если хотя бы одного нет - сбрасываем флаг
            if is_active:
                target.memory["axis_buff_triad_active"] = False

        # === 2. НЕГАТИВНАЯ ТРИАДА (Weakness, Paralysis, Slow) ===
        has_weak = target.get_status("weakness") >= 1
        has_para = target.get_status("paralysis") >= 1
        has_slow = target.get_status("slow") >= 1

        is_active_debuff = target.memory.get("axis_debuff_triad_active", False)

        if has_weak and has_para and has_slow:
            if not is_active_debuff:
                d_weak = self._get_max_duration(target, "weakness")
                d_para = self._get_max_duration(target, "paralysis")
                d_slow = self._get_max_duration(target, "slow")

                target.add_status("weakness", 1, duration=d_weak, trigger_events=False)
                target.add_status("paralysis", 1, duration=d_para, trigger_events=False)
                target.add_status("slow", 1, duration=d_slow, trigger_events=False)

                target.memory["axis_debuff_triad_active"] = True
                logger.log(f"⛓️ Axis Unity: Debuff Triad activated on {target.name}", LogLevel.NORMAL, "Passive")
        else:
            if is_active_debuff:
                target.memory["axis_debuff_triad_active"] = False

    # --- ХУКИ ---

    def on_status_applied(self, unit, status_id, amount, **kwargs):
        """Когда статус накладывается на САМОГО Аксиса (владельца пассивки)."""
        self._evaluate_triad(unit)

    def on_status_applied_global(self, unit, target, status_id, amount, **kwargs):
        """
        Новый хук! Срабатывает, когда статус накладывается на ЛЮБОГО ДРУГОГО юнита (target).
        unit - это Аксис (наблюдатель).
        target - это тот, кто получил статус.
        """
        self._evaluate_triad(target)

    def on_round_start(self, unit, log_func, allies=None, enemies=None, **kwargs):
        """Контрольная проверка в начале раунда для всех."""
        all_units = [unit]
        if allies: all_units.extend(allies)
        if enemies: all_units.extend(enemies)

        for u in all_units:
            self._evaluate_triad(u)

# === НОВЫЕ ПАССИВКИ (СИЛЬНЫЕ СТОРОНЫ) ===

class PassivePseudoProtagonist(BasePassive):
    id = "pseudo_protagonist"
    name = "Псевдо-главный герой"
    description = (
        "Вне боя Аксис получает опыт за каждый брошенный кубик, "
        "равный его значению, вне зависимости от результата."
    )
    is_active_ability = False

    # TODO: Реализовать хук on_dice_rolled (вне боя)
    def on_out_of_combat_roll(self, unit, roll_result):
        pass


class PassiveSourceAccess(BasePassive):
    id = "source_access"
    name = "Доступ к истокам"
    description = (
        "В бою все кубики (кроме скорости) зависят не от характеристик, "
        "а от Удачи (Luck). (Соотношение TBD: 1 к 5 или 1 к 10)."
    )
    is_active_ability = False

    # TODO: Реализовать подмену атрибута при расчете силы кубика
    def modify_dice_stat_dependency(self, unit, dice_obj):
        pass


class PassiveMetaAwareness(BasePassive):
    id = "meta_awareness"
    name = "Мета осознание"
    description = (
        "Персонаж может ломать четвёртую стену, читать посты и даже НРП чаты. "
        "Знание - сила, даже если оно не должно существовать."
    )
    is_active_ability = False
    # Чисто РП пассивка, механики не требует


# === НОВЫЕ ПАССИВКИ (СЛАБЫЕ СТОРОНЫ) ===

class PassiveChthonic(BasePassive):
    id = "chthonic_nature"
    name = "Хтонь"
    description = "Любой бросок Красноречия проходит с Помехой (Disadvantage)."
    is_active_ability = False

    # TODO: Реализовать наложение помехи на скиллчеки красноречия
    def on_check_roll(self, unit, attribute, context):
        pass