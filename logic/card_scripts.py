import math
import random
import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.context import RollContext


# ==========================================
# 🧮 УНИВЕРСАЛЬНЫЙ КАЛЬКУЛЯТОР
# ==========================================

def _get_unit_stat(unit, stat_name: str) -> int:
    """
    Извлекает значение характеристики, навыка, ресурса или текущего состояния.
    """
    if not unit or not stat_name: return 0
    stat_name = stat_name.lower()

    # 1. Текущие параметры
    if stat_name == "hp" or stat_name == "current_hp": return unit.current_hp
    if stat_name == "sp" or stat_name == "current_sp": return unit.current_sp
    if stat_name == "stagger" or stat_name == "current_stagger": return unit.current_stagger

    # 2. Максимальные параметры
    if stat_name == "max_hp": return unit.max_hp
    if stat_name == "max_sp": return unit.max_sp
    if stat_name == "max_stagger": return unit.max_stagger

    # 3. Ресурсы (Luck, Charge и т.д.)
    if stat_name in unit.resources: return unit.resources[stat_name]
    if stat_name == "luck": return unit.skills.get("luck", 0)  # Фоллбек на навык

    # 4. Атрибуты и Навыки (с учетом баффов/модификаторов)
    # Пытаемся найти в modifiers (total_X), затем в attributes, затем в skills

    # Ищем в modifiers (новая структура {'flat': val, 'pct': val} или старая int)
    val_data = unit.modifiers.get(stat_name)
    if val_data is None:
        val_data = unit.modifiers.get(f"total_{stat_name}")  # Совместимость

    if val_data is not None:
        if isinstance(val_data, dict): return int(val_data.get("flat", 0))
        return int(val_data)

    # Ищем в базе
    if stat_name in unit.attributes: return unit.attributes[stat_name]
    if stat_name in unit.skills: return unit.skills[stat_name]

    return 0


def _resolve_value(source, target, params: dict) -> int:
    """
    Главная формула:
    Result = Base + ( (SourceStat - TargetStat?) * Factor )
    """
    base = params.get("base", 0)
    if isinstance(base, float): base = int(base)  # Защита от float инпутов

    stat_key = params.get("stat", None)  # Например: "strength", "eloquence", "max_hp"

    if not stat_key or stat_key == "None":
        return base

    # Получаем стат источника
    source_val = _get_unit_stat(source, stat_key)

    # Если нужно считать разницу (Source - Target)
    if params.get("diff", False) and target:
        target_val = _get_unit_stat(target, stat_key)
        final_stat = source_val - target_val
        # Опционально: не уходить в минус? Обычно разница может быть отрицательной (штраф)
    else:
        final_stat = source_val

    factor = float(params.get("factor", 1.0))

    # Считаем бонус
    bonus = final_stat * factor

    return int(base + bonus)


def _get_targets(ctx, target_mode):
    """Возвращает список целей на основе режима."""
    if target_mode == "self":
        return [ctx.source] if ctx.source else []
    elif target_mode == "target":
        return [ctx.target] if ctx.target else []
    elif target_mode == "all":
        # В контексте 1 на 1 это оба.
        # В массовом бою тут нужна логика получения команд через st.session_state
        res = []
        if ctx.source: res.append(ctx.source)
        if ctx.target: res.append(ctx.target)
        return res
    elif target_mode == "all_allies":
        # Попытка найти всех союзников
        source = ctx.source
        my_team = []
        if 'team_left' in st.session_state and source in st.session_state['team_left']:
            my_team = st.session_state['team_left']
        elif 'team_right' in st.session_state and source in st.session_state['team_right']:
            my_team = st.session_state['team_right']

        if not my_team: return [source]
        return [u for u in my_team if not u.is_dead()]

    return []


# ==========================================
# 📜 НОВЫЕ УНИВЕРСАЛЬНЫЕ СКРИПТЫ
# ==========================================

def modify_roll_power(context: 'RollContext', params: dict):
    """
    Изменяет силу броска.
    Заменяет: eloquence_clash, add_hp_damage, luck_bonus (частично).
    """
    amount = _resolve_value(context.source, context.target, params)
    reason = params.get("reason", "Bonus")

    if amount != 0:
        stat_name = params.get("stat", "")
        if stat_name: reason = f"{stat_name.title()} ({amount})"
        context.modify_power(amount, reason)


def deal_effect_damage(context: 'RollContext', params: dict):
    """
    Наносит прямой урон (эффектом).
    Заменяет: self_harm_percent, deal_custom_damage.
    """
    dmg_type = params.get("type", "hp")  # hp / stagger / sp
    targets = _get_targets(context, params.get("target", "target"))

    amount = _resolve_value(context.source, context.target, params)
    if amount <= 0: return

    for u in targets:
        if dmg_type == "hp":
            u.current_hp = max(0, u.current_hp - amount)
            context.log.append(f"💔 **{u.name}**: -{amount} HP (Effect)")
        elif dmg_type == "stagger":
            u.current_stagger = max(0, u.current_stagger - amount)
            context.log.append(f"😵 **{u.name}**: -{amount} Stagger")
        elif dmg_type == "sp":
            # Используем встроенный метод для SP (он учитывает панику)
            u.take_sanity_damage(amount)
            context.log.append(f"🤯 **{u.name}**: -{amount} SP")


def restore_resource(context: 'RollContext', params: dict):
    """
    Восстанавливает HP/SP/Stagger.
    Заменяет: restore_hp, restore_sp.
    """
    res_type = params.get("type", "hp")
    targets = _get_targets(context, params.get("target", "self"))

    amount = _resolve_value(context.source, context.target, params)
    # Если amount отрицательный, это работает как урон (но лучше использовать deal_effect_damage)

    for u in targets:
        if res_type == "hp":
            healed = u.heal_hp(amount)
            context.log.append(f"💚 **{u.name}**: +{healed} HP")
        elif res_type == "sp":
            recovered = u.restore_sp(amount)
            context.log.append(f"🧠 **{u.name}**: +{recovered} SP")
        elif res_type == "stagger":
            old = u.current_stagger
            u.current_stagger = min(u.max_stagger, u.current_stagger + amount)
            context.log.append(f"🛡️ **{u.name}**: +{u.current_stagger - old} Stagger")


def apply_status(context: 'RollContext', params: dict):
    """
    Накладывает статус.
    Теперь stack тоже может скейлиться от статов!
    """
    status_name = params.get("status")
    if not status_name: return

    target_mode = params.get("target", "target")
    duration = int(params.get("duration", 1))

    # Вычисляем количество стаков через универсальную формулу
    # Обычно base=Stack из эдитора.
    stack = _resolve_value(context.source, context.target, params)

    if stack <= 0: return

    targets = _get_targets(context, target_mode)

    # Хак для дыма
    if status_name == "smoke": duration = 99

    for u in targets:
        # Проверка иммунитета (Red Lycoris и т.д.)
        if u.get_status("red_lycoris") > 0 and status_name != "red_lycoris":
            context.log.append(f"🚫 {u.name} Immune to {status_name}")
            continue

        success, msg = u.add_status(status_name, stack, duration=duration)
        if success:
            context.log.append(f"🧪 **{u.name}**: +{stack} {status_name.capitalize()}")
        elif msg:
            context.log.append(f"🛡️ {msg}")


def steal_status(context: 'RollContext', params: dict):
    status_name = params.get("status")
    thief, victim = context.source, context.target
    if not thief or not victim: return

    current = victim.get_status(status_name)
    if current > 0:
        victim.remove_status(status_name, current)
        duration = 99 if status_name == "smoke" else 1
        thief.add_status(status_name, current, duration=duration)
        context.log.append(f"✋ **{thief.name}** stole {current} {status_name}")


def multiply_status(context: 'RollContext', params: dict):
    status_name = params.get("status")
    multiplier = float(params.get("multiplier", 2.0))
    targets = _get_targets(context, params.get("target", "target"))

    for u in targets:
        current = u.get_status(status_name)
        if current > 0:
            add = int(current * (multiplier - 1))
            duration = 99 if status_name == "smoke" else 1
            u.add_status(status_name, add, duration=duration)
            context.log.append(f"✖️ **{u.name}**: {status_name} x{multiplier} (+{add})")


# ==========================================
# 📖 REGISTRY
# ==========================================

SCRIPTS_REGISTRY = {
    # Новые универсальные
    "modify_roll_power": modify_roll_power,
    "deal_effect_damage": deal_effect_damage,
    "restore_resource": restore_resource,
    "apply_status": apply_status,

    # Утилитарные
    "steal_status": steal_status,
    "multiply_status": multiply_status,

    # Старые (Mapped to new logic inside functions or kept for specific logic)
    # Мы можем оставить старые имена ключей в реестре, но направить их на новые функции,
    # если параметры совместимы. Но лучше обновить Editor.
}