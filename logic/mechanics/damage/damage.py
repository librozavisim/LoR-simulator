from core.logging import logger, LogLevel
from logic.calculations.base_calc import get_modded_value

# Импортируем из новых модулей
from logic.mechanics.damage.damage_utils import _get_attack_info, _apply_resource_damage
from logic.mechanics.damage.damage_calc import _calculate_resistance, _calculate_outgoing_damage


def _apply_stagger_side_damage(target, attacker_ctx, final_amt):
    """Наносит побочный урон по Stagger при получении HP урона."""
    if target.is_staggered() or target.get_status("red_lycoris") > 0:
        return

    dtype, dice_obj = _get_attack_info(attacker_ctx)

    res_stg, _ = _calculate_resistance(
        target, attacker_ctx, dtype, dice_obj,
        log_list=attacker_ctx.log
    )

    stg_base_amt = final_amt

    if hasattr(target, "apply_mechanics_filter"):
        stg_base_amt = target.apply_mechanics_filter("modify_incoming_damage", stg_base_amt, damage_type="hp")

    stat_reduction = get_modded_value(0, "damage_take", target.modifiers)
    stg_after_def = max(0, stg_base_amt - stat_reduction)

    stg_dmg = int(stg_after_def * res_stg)

    stg_take_pct = target.modifiers["stagger_take"]["pct"]
    if stg_take_pct != 0:
        mod_mult = 1.0 + (stg_take_pct / 100.0)
        stg_dmg = int(stg_dmg * mod_mult)

    target.current_stagger = max(0, target.current_stagger - stg_dmg)
    logger.log(f"😵 {target.name} took {stg_dmg} Stagger Side-Damage (Res: {res_stg:.2f})", LogLevel.MINIMAL, "Damage")


def deal_direct_damage(source_ctx, target, amount: int, dmg_type: str, trigger_event_func):
    """Наносит прямой урон (эффекты, скрипты и т.д.) без конвертации типов."""
    if amount <= 0: return

    initial_amount = amount

    if hasattr(target, "apply_mechanics_filter"):
        amount = target.apply_mechanics_filter("modify_incoming_damage", amount, damage_type=dmg_type)

    if amount <= 0 < initial_amount:
        if source_ctx: source_ctx.log.append("🛡️ Damage mitigated to 0")
        return

    final_dmg = 0
    dtype_name, dice_obj = _get_attack_info(source_ctx)
    log_list = source_ctx.log if source_ctx else None

    if dmg_type == "hp":
        stat_reduction = get_modded_value(0, "damage_take", target.modifiers)
        amount_after_def = max(0, amount - stat_reduction)

        res, is_stag_hit = _calculate_resistance(target, source_ctx, dtype_name, dice_obj, log_list)
        final_dmg = int(amount_after_def * res)

        threshold = get_modded_value(0, "damage_threshold", target.modifiers)

        if final_dmg < threshold:
            if log_list is not None: log_list.append(f"🛡️ Ignored (<{threshold})")
            final_dmg = 0
        else:
            # === [ВАЖНО] Поглощение барьером для HP ===
            if hasattr(target, "apply_mechanics_filter"):
                final_dmg = target.apply_mechanics_filter("absorb_damage", final_dmg, damage_type=dmg_type,
                                                          log_list=log_list)

            prefix = ""
            if stat_reduction != 0: prefix += f"[-{stat_reduction} Skin] "
            prefix += f"[x{res:.1f} Res] "

            _apply_resource_damage(target, final_dmg, "hp", source_ctx, log_prefix=prefix)

    elif dmg_type == "stagger":
        res = getattr(target.hp_resists, dtype_name, 1.0)
        stg_take_pct = target.modifiers["stagger_take"]["pct"]
        mod_mult = 1.0 + (stg_take_pct / 100.0)

        final_dmg = int(amount * res * mod_mult)

        # === [ВАЖНО] Поглощение барьером для Stagger ===
        if hasattr(target, "apply_mechanics_filter"):
            final_dmg = target.apply_mechanics_filter("absorb_damage", final_dmg, damage_type=dmg_type,
                                                      log_list=log_list)

        target.current_stagger = max(0, target.current_stagger - final_dmg)

        if source_ctx: source_ctx.log.append(f"😵 **{target.name}**: Stagger -{final_dmg}")
        logger.log(f"😵 {target.name} took {final_dmg} Stagger Damage", LogLevel.MINIMAL, "Damage")

    if initial_amount > 0:
        extra_args = {"raw_amount": initial_amount}
        if dice_obj: extra_args["damage_type"] = dice_obj.dtype

        log_wrapper = lambda msg: source_ctx.log.append(msg) if source_ctx else None

        trigger_event_func(
            "on_take_damage",
            target,
            final_dmg,
            source_ctx.source if source_ctx else None,
            log_func=log_wrapper,
            dmg_type=dmg_type,
            **extra_args
        )


def apply_damage(attacker_ctx, defender_ctx, dmg_type="hp",
                 trigger_event_func=None, script_runner_func=None):
    """
    Основной пайплайн нанесения урона от атаки.
    """
    attacker = attacker_ctx.source
    defender = attacker_ctx.target
    if defender_ctx: defender = defender_ctx.source

    if not defender: return

    if hasattr(defender, "iter_mechanics"):
        for mech in defender.iter_mechanics():
            if mech.prevents_damage(defender, attacker_ctx):
                attacker_ctx.log.append(f"🚫 {defender.name} Immune ({mech.name if hasattr(mech, 'name') else mech.id})")
                logger.log(f"🚫 {defender.name} Immune to Damage ({mech.id})", LogLevel.MINIMAL, "Damage")
                return

    if hasattr(attacker, "trigger_mechanics"):
        attacker.trigger_mechanics("on_hit", attacker_ctx)
    if script_runner_func:
        script_runner_func("on_hit", attacker_ctx)

    final_amt = _calculate_outgoing_damage(attacker, attacker_ctx, dmg_type)

    convert_to_sp = getattr(attacker_ctx, 'convert_hp_to_sp', False)

    if dmg_type == "hp":
        if convert_to_sp:
            sp_damage = final_amt
            if hasattr(defender, "apply_mechanics_filter"):
                sp_damage = defender.apply_mechanics_filter(
                    "modify_incoming_damage",
                    sp_damage,
                    damage_type="sp",
                    log_list=attacker_ctx.log
                )
            _apply_resource_damage(defender, sp_damage, "sp", attacker_ctx)
        else:
            deal_direct_damage(attacker_ctx, defender, final_amt, "hp", trigger_event_func)

    elif dmg_type == "stagger":
        deal_direct_damage(attacker_ctx, defender, final_amt, "stagger", trigger_event_func)

    if dmg_type == "hp":
        _apply_stagger_side_damage(defender, attacker_ctx, final_amt)