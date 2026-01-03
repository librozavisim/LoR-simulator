from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from logic.context import RollContext


# ==========================================
# 🧮 УНИВЕРСАЛЬНЫЙ КАЛЬКУЛЯТОР (CORE)
# ==========================================

def _get_unit_stat(unit, stat_name: str) -> int:
    """
    Умное получение значения стата.
    """
    if not unit or not stat_name: return 0
    key = stat_name.lower()

    # 1. Динамические параметры
    if key in ["hp", "current_hp"]: return unit.current_hp
    if key in ["sp", "current_sp"]: return unit.current_sp
    if key in ["stagger", "current_stagger"]: return unit.current_stagger

    if key == "max_hp": return unit.max_hp
    if key == "max_sp": return unit.max_sp
    if key == "max_stagger": return unit.max_stagger

    # 2. Ресурсы
    if key in unit.resources: return unit.resources[key]
    if key == "luck": return unit.skills.get("luck", 0)

    # 3. Атрибуты и Навыки (через modifiers)
    val_data = unit.modifiers.get(key)
    if val_data is None:
        val_data = unit.modifiers.get(f"total_{key}")

    if val_data is not None:
        if isinstance(val_data, dict): return int(val_data.get("flat", 0))
        return int(val_data)

    if key in unit.attributes: return unit.attributes[key]
    if key in unit.skills: return unit.skills[key]

    return 0


def _resolve_value(source, target, params: dict) -> int:
    """
    Универсальная формула вычисления значения.
    Поддерживает scale_from_target для расчета от статов цели.
    """
    # 1. Базовое значение
    base = int(params.get("base", params.get("amount", 0)))

    # 2. Стат для скалирования
    stat_key = params.get("stat")
    if not stat_key or stat_key == "None":
        return base

    # 3. Определение источника стата
    # Если scale_from_target=True, берем стат у TARGET (того, на кого применяется эффект)
    scale_from_target = params.get("scale_from_target", False)

    primary_unit = target if scale_from_target else source
    secondary_unit = source if scale_from_target else target

    # Защита на случай, если юнита нет (например target умер или None)
    if not primary_unit:
        return base

    primary_val = _get_unit_stat(primary_unit, stat_key)
    final_stat_val = primary_val

    # 4. Разница (если включено)
    # Если scale_from_target=True, то diff будет (Target - Source)
    if params.get("diff", False) and secondary_unit:
        secondary_val = _get_unit_stat(secondary_unit, stat_key)
        final_stat_val = primary_val - secondary_val

    # 5. Множитель
    factor = float(params.get("factor", 1.0))

    total = base + (final_stat_val * factor)
    return int(total)


def _get_targets(ctx, target_mode: str):
    """Определяет список целей."""
    if target_mode == "self":
        return [ctx.source] if ctx.source else []
    elif target_mode == "target":
        return [ctx.target] if ctx.target else []
    elif target_mode == "all":
        res = []
        if ctx.source: res.append(ctx.source)
        if ctx.target: res.append(ctx.target)
        return res
    elif target_mode == "all_allies":
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
# 📜 СКРИПТЫ
# ==========================================

def modify_roll_power(ctx: 'RollContext', params: dict):
    amount = _resolve_value(ctx.source, ctx.target, params)
    if amount == 0: return

    reason = params.get("reason", "Bonus")
    if reason == "Bonus" and params.get("stat"):
        reason = f"{params['stat'].title()} scale"

    ctx.modify_power(amount, reason)


def deal_effect_damage(ctx: 'RollContext', params: dict):
    dmg_type = params.get("type", "hp")
    targets = _get_targets(ctx, params.get("target", "target"))

    for u in targets:
        # Считаем урон индивидуально для каждой цели (если вдруг скейл от цели)
        amount = _resolve_value(ctx.source, u, params)
        if amount <= 0: continue

        if dmg_type == "hp":
            u.current_hp = max(0, u.current_hp - amount)
            ctx.log.append(f"💔 **{u.name}**: -{amount} HP (Effect)")
        elif dmg_type == "stagger":
            u.current_stagger = max(0, u.current_stagger - amount)
            ctx.log.append(f"😵 **{u.name}**: -{amount} Stagger")
        elif dmg_type == "sp":
            u.take_sanity_damage(amount)
            ctx.log.append(f"🤯 **{u.name}**: -{amount} SP")


def restore_resource(ctx: 'RollContext', params: dict):
    res_type = params.get("type", "hp")
    targets = _get_targets(ctx, params.get("target", "self"))

    for u in targets:
        # Считаем лечение индивидуально (например 25% от Макс ХП цели)
        amount = _resolve_value(ctx.source, u, params)

        if res_type == "hp":
            if amount >= 0:
                healed = u.heal_hp(amount)
                ctx.log.append(f"💚 **{u.name}**: +{healed} HP")
            else:
                u.current_hp = max(0, u.current_hp + amount)
                ctx.log.append(f"💔 **{u.name}**: {amount} HP")

        elif res_type == "sp":
            if amount >= 0:
                recovered = u.restore_sp(amount)
                ctx.log.append(f"🧠 **{u.name}**: +{recovered} SP")
            else:
                u.take_sanity_damage(abs(amount))
                ctx.log.append(f"🤯 **{u.name}**: {amount} SP")

        elif res_type == "stagger":
            old = u.current_stagger
            u.current_stagger = min(u.max_stagger, u.current_stagger + amount)
            diff = u.current_stagger - old
            ctx.log.append(f"🛡️ **{u.name}**: +{diff} Stagger")


def apply_status(ctx: 'RollContext', params: dict):
    status_name = params.get("status")
    if not status_name: return

    target_mode = params.get("target", "target")
    duration = int(params.get("duration", 1))
    min_roll = int(params.get("min_roll", 0))

    if min_roll > 0 and ctx.final_value < min_roll:
        return

    # Подготовка параметров для расчета
    calc_params = params.copy()
    if "stack" in params and "base" not in params:
        calc_params["base"] = params["stack"]

    targets = _get_targets(ctx, target_mode)
    if status_name == "smoke": duration = 99

    for u in targets:
        if u.get_status("red_lycoris") > 0 and status_name != "red_lycoris":
            ctx.log.append(f"🚫 {u.name} Immune to {status_name}")
            continue

        # ВАЖНО: Считаем стаки для КОНКРЕТНОГО юнита u
        # Если scale_from_target=True, то стат возьмется у u
        stack = _resolve_value(ctx.source, u, calc_params)

        if stack <= 0: continue

        success, msg = u.add_status(status_name, stack, duration=duration)
        if success:
            ctx.log.append(f"🧪 **{u.name}**: +{stack} {status_name.capitalize()}")
        elif msg:
            ctx.log.append(f"🛡️ {msg}")


def steal_status(ctx: 'RollContext', params: dict):
    status_name = params.get("status")
    thief, victim = ctx.source, ctx.target
    if not thief or not victim: return

    current = victim.get_status(status_name)
    if current > 0:
        victim.remove_status(status_name, current)
        duration = 99 if status_name == "smoke" else 1
        thief.add_status(status_name, current, duration=duration)
        ctx.log.append(f"✋ **{thief.name}** stole {current} {status_name}")


def multiply_status(ctx: 'RollContext', params: dict):
    status_name = params.get("status")
    multiplier = float(params.get("multiplier", 2.0))
    targets = _get_targets(ctx, params.get("target", "target"))

    for u in targets:
        current = u.get_status(status_name)
        if current > 0:
            add = int(current * (multiplier - 1))
            duration = 99 if status_name == "smoke" else 1
            u.add_status(status_name, add, duration=duration)
            ctx.log.append(f"✖️ **{u.name}**: {status_name} x{multiplier} (+{add})")


SCRIPTS_REGISTRY = {
    "modify_roll_power": modify_roll_power,
    "deal_effect_damage": deal_effect_damage,
    "restore_resource": restore_resource,
    "apply_status": apply_status,
    "steal_status": steal_status,
    "multiply_status": multiply_status,
}