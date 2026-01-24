from core.enums import DiceType
from core.logging import logger, LogLevel


def resolve_counter_clash(engine, source, target, die_atk, die_cnt, adv_atk):
    """
    Решает столкновение Атаки против Активного Контр-кубика.
    Возвращает: outcome_dict { outcome_str, details_list, counter_spent_bool }
    """
    target.current_die = die_cnt
    ctx_atk = engine._create_roll_context(source, target, die_atk, is_disadvantage=adv_atk)
    ctx_cnt = engine._create_roll_context(target, source, die_cnt)

    ctx_atk.opponent_ctx = ctx_cnt
    ctx_cnt.opponent_ctx = ctx_atk

    val_atk = ctx_atk.final_value
    val_cnt = ctx_cnt.final_value

    details = ctx_atk.log + ctx_cnt.log
    outcome = ""
    counter_spent = True  # По умолчанию тратится, если не выиграл/ничья

    is_atk_def = die_atk.dtype in [DiceType.BLOCK, DiceType.EVADE]
    is_cnt_def = die_cnt.dtype in [DiceType.BLOCK, DiceType.EVADE]

    if is_atk_def and is_cnt_def:
        outcome = "🛡️ Defensive Clash (Both Spent)"

    elif val_cnt > val_atk:
        # Counter Wins
        engine._handle_clash_win(ctx_cnt)
        engine._handle_clash_lose(ctx_atk)

        if die_cnt.dtype == DiceType.EVADE:
            outcome = f"⚡ Stored Evade! (Recycle)"
            rec = target.restore_stagger(val_cnt)
            details.append(f"🛡️ +{rec} Stagger")
            counter_spent = False  # Evade возвращается
        else:
            outcome = f"⚡ Counter Hit"
            engine._resolve_clash_interaction(ctx_cnt, ctx_atk, val_cnt - val_atk)

    elif val_atk > val_cnt:
        # Attack Wins
        outcome = f"💥 Counter Broken"
        engine._handle_clash_win(ctx_atk)
        engine._handle_clash_lose(ctx_cnt)

        if die_atk.dtype not in [DiceType.BLOCK, DiceType.EVADE]:
            engine._resolve_clash_interaction(ctx_atk, ctx_cnt, val_atk - val_cnt)

    else:
        outcome = "🤝 Draw (Counter Broken)"

    return {
        "outcome": outcome,
        "details": details,
        "counter_spent": counter_spent,
        "val_atk": val_atk,
        "val_cnt": val_cnt,
        "atk_ctx": ctx_atk  # Нужен, если вдруг захотим нанести урон
    }


def resolve_passive_defense(engine, source, target, die_atk, die_def, adv_atk, adv_def):
    """
    Решает столкновение Атаки против Защитного кубика в слоте (Passive).
    """
    target.current_die = die_def
    ctx_atk = engine._create_roll_context(source, target, die_atk, is_disadvantage=adv_atk)
    ctx_def = engine._create_roll_context(target, source, die_def, is_disadvantage=adv_def)

    ctx_atk.opponent_ctx = ctx_def
    ctx_def.opponent_ctx = ctx_atk

    val_atk = ctx_atk.final_value
    val_def = ctx_def.final_value

    outcome = ""
    is_atk_def = die_atk.dtype in [DiceType.BLOCK, DiceType.EVADE]

    if is_atk_def:
        outcome = "🛡️ Defensive Clash (Both Spent)"
    elif val_atk > val_def:
        outcome = f"🗡️ Atk Break"
        engine._handle_clash_win(ctx_atk)
        engine._handle_clash_lose(ctx_def)
        engine._resolve_clash_interaction(ctx_atk, ctx_def, val_atk - val_def)
    elif val_def > val_atk:
        outcome = f"🛡️ Defended"
        engine._handle_clash_win(ctx_def)
        engine._handle_clash_lose(ctx_atk)
        engine._resolve_clash_interaction(ctx_def, ctx_atk, val_def - val_atk)
    else:
        outcome = "🤝 Draw"
        engine._handle_clash_draw(ctx_atk)
        engine._handle_clash_draw(ctx_def)

    return {
        "outcome": outcome,
        "details": ctx_atk.log + ctx_def.log,
        "val_atk": val_atk,
        "val_def": val_def
    }


def resolve_unopposed_hit(engine, source, target, die_atk, adv_atk, flags):
    """
    Решает безответный удар (Unopposed).
    """
    outcome = "Unopposed"
    if flags.get("is_redirected"):
        outcome += " (Redirected)"
    elif flags.get("destroy_def"):
        outcome += " (Speed Break)"

    ctx_atk = engine._create_roll_context(source, target, die_atk, is_disadvantage=adv_atk)

    ATK_TYPES = [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]

    if die_atk.dtype in ATK_TYPES:
        logger.log(f"⚔️ Direct Hit! {ctx_atk.final_value} Dmg", LogLevel.NORMAL, "OneSided")
        engine._apply_damage(ctx_atk, None, "hp")

    elif die_atk.dtype == DiceType.EVADE:
        if not hasattr(source, 'stored_dice') or not isinstance(source.stored_dice, list):
            source.stored_dice = []
        source.stored_dice.append(die_atk)
        outcome = "🏃 Evade Stored"
        logger.log("🏃 Evade die stored (Unopposed)", LogLevel.VERBOSE, "OneSided")

    elif die_atk.dtype == DiceType.BLOCK:
        outcome = "🛡️ Block (Ignored)"
        logger.log("🛡️ Offensive Block ignored", LogLevel.VERBOSE, "OneSided")
    else:
        outcome += " (Skipped)"

    return {
        "outcome": outcome,
        "details": ctx_atk.log,
        "val_atk": ctx_atk.final_value
    }