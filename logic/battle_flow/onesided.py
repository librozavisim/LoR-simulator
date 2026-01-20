from core.enums import DiceType
from logic.battle_flow.speed import calculate_speed_advantage
from core.logging import logger, LogLevel


def process_onesided(engine, source, target, round_label, spd_atk, spd_d, intent_atk=True, is_redirected=False):
    report = []
    card = source.current_card
    def_card = target.current_card

    logger.log(f"One-Sided: {source.name} vs {target.name} (Spd: {spd_atk} vs {spd_d}, Redir={is_redirected})",
               LogLevel.VERBOSE, "OneSided")

    # Расчет преимущества скорости
    adv_atk, adv_def, _, destroy_def = calculate_speed_advantage(spd_atk, spd_d, intent_atk, True)

    if destroy_def:
        logger.log(f"Speed Advantage: {source.name} breaks {target.name}'s defense die", LogLevel.VERBOSE, "OneSided")

    source_immune = False
    if hasattr(source, "iter_mechanics"):
        for mech in source.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(source):
                source_immune = True
                break

    # Проверяем иммунитет ЗАЩИТНИКА (target)
    target_immune = False
    if hasattr(target, "iter_mechanics"):
        for mech in target.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(target):
                target_immune = True
                break

    # 1. Break Check (Empty Slot Break)
    defender_breaks_attacker = False
    if not def_card:
        if spd_d - spd_atk >= 8:
            if hasattr(target, "iter_mechanics"):
                for mech in target.iter_mechanics():
                    if hasattr(mech, "can_break_empty_slot") and mech.can_break_empty_slot(target):
                        # [FIX] Если у атакующего иммунитет - не ломаем
                        if source_immune:
                            logger.log(f"🛡️ Empty Slot Break prevented by Immunity for {source.name}", LogLevel.VERBOSE,
                                       "OneSided")
                        else:
                            defender_breaks_attacker = True
                            logger.log(f"Empty Slot Break: {target.name} breaks {source.name} (Spd Diff > 8)",
                                       LogLevel.VERBOSE, "OneSided")
                        break

    # 2. Prevent Destruction (Target)
    if destroy_def and target_immune:
        destroy_def = False
        adv_atk = True
        logger.log(f"Destruction Prevented for {target.name} (Immunity)", LogLevel.VERBOSE, "OneSided")

    on_use_logs = []
    engine._process_card_self_scripts("on_use", source, target, custom_log_list=on_use_logs)

    attacker_queue = list(card.dice_list)
    att_idx = 0
    active_counter_die = None


    def fetch_next_counter(unit):
        # 1. Stored Dice
        if hasattr(unit, 'stored_dice') and isinstance(unit.stored_dice, list) and unit.stored_dice:
            if unit.is_staggered():
                can_use = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.can_use_counter_die_while_staggered(unit):
                            can_use = True
                            break
                if not can_use: return None
            logger.log(f"{unit.name} retrieves Stored Die", LogLevel.VERBOSE, "OneSided")
            return unit.stored_dice.pop(0)

        # 2. Counter Dice
        if unit.counter_dice:
            if unit.is_staggered():
                can_use = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.can_use_counter_die_while_staggered(unit):
                            can_use = True
                            break
                if not can_use: return None
            logger.log(f"{unit.name} retrieves Counter Die", LogLevel.VERBOSE, "OneSided")
            return unit.counter_dice.pop(0)
        return None

    max_iter = 20
    cur_iter = 0

    while att_idx < len(attacker_queue) and cur_iter < max_iter:
        cur_iter += 1
        die = attacker_queue[att_idx]

        if source.is_dead() or target.is_dead() or source.is_staggered():
            logger.log("One-Sided flow interrupted (Death/Stagger)", LogLevel.VERBOSE, "OneSided")
            break

        source.current_die = die

        detail_logs = []
        if att_idx == 0 and on_use_logs: detail_logs.extend(on_use_logs)

        # A. Break Check
        if defender_breaks_attacker:
            logger.log(f"Attacker Die {att_idx + 1} Broken by Speed", LogLevel.NORMAL, "OneSided")
            report.append({
                "type": "onesided",
                "round": f"{round_label} (Break)",
                "left": {"unit": source.name, "card": card.name, "dice": "🚫 Broken", "val": 0, "range": "-"},
                "right": {"unit": target.name, "card": "-", "dice": "⚡ Break", "val": 0, "range": "-"},
                "outcome": "🚫 Broken (Speed)", "details": detail_logs + ["Def Speed > 8: Die Destroyed"]
            })
            att_idx += 1
            continue

        ctx_atk = engine._create_roll_context(source, target, die, is_disadvantage=adv_atk)

        # B. Get Defense
        if not active_counter_die:
            active_counter_die = fetch_next_counter(target)

        # C. РЕЗОЛВ ЗАЩИТЫ (COUNTER CLASH)
        if active_counter_die:
            target.current_die = active_counter_die
            ctx_cnt = engine._create_roll_context(target, source, active_counter_die)

            ctx_atk.opponent_ctx = ctx_cnt
            ctx_cnt.opponent_ctx = ctx_atk

            val_atk = ctx_atk.final_value
            val_cnt = ctx_cnt.final_value

            logger.log(f"Counter Clash: Atk({val_atk}) vs Cnt({val_cnt})", LogLevel.VERBOSE, "OneSided")

            outcome = ""

            # [FIX] Проверка на взаимную защиту (Evade/Block vs Evade/Block)
            is_atk_def = die.dtype in [DiceType.BLOCK, DiceType.EVADE]
            is_cnt_def = active_counter_die.dtype in [DiceType.BLOCK, DiceType.EVADE]

            if is_atk_def and is_cnt_def:
                outcome = "🛡️ Defensive Clash (Both Spent)"
                active_counter_die = None  # Контр потрачен

            elif val_cnt > val_atk:
                # Counter Wins
                engine._handle_clash_win(ctx_cnt)
                engine._handle_clash_lose(ctx_atk)

                if active_counter_die.dtype == DiceType.EVADE:
                    outcome = f"⚡ Stored Evade! (Recycle)"
                    rec = target.restore_stagger(val_cnt)
                    detail_logs.append(f"🛡️ +{rec} Stagger")
                else:
                    outcome = f"⚡ Counter Hit"
                    engine._resolve_clash_interaction(ctx_cnt, ctx_atk, val_cnt - val_atk)
                    active_counter_die = None

            elif val_atk > val_cnt:
                # Attack Wins
                outcome = f"💥 Counter Broken"
                engine._handle_clash_win(ctx_atk)
                engine._handle_clash_lose(ctx_cnt)

                if die.dtype not in [DiceType.BLOCK, DiceType.EVADE]:
                    engine._resolve_clash_interaction(ctx_atk, ctx_cnt, val_atk - val_cnt)

                active_counter_die = None

            else:
                # Draw
                outcome = "🤝 Draw (Counter Broken)"
                active_counter_die = None

            logger.log(f"Counter Result: {outcome}", LogLevel.NORMAL, "OneSided")

            l_lbl = die.dtype.name
            r_lbl = f"{active_counter_die.dtype.name if active_counter_die else 'Broken'} (Cnt)"

            report.append({
                "type": "clash",
                "round": f"{round_label} (Counter)",
                "left": {"unit": source.name, "card": card.name, "dice": l_lbl, "val": val_atk, "range": "-"},
                "right": {"unit": target.name, "card": "Stored", "dice": r_lbl, "val": val_cnt, "range": "-"},
                "outcome": outcome, "details": detail_logs + ctx_atk.log + ctx_cnt.log
            })

            att_idx += 1
            continue

        # D. ПАССИВНАЯ ЗАЩИТА
        def_die = None
        slot_idx = att_idx

        if not is_redirected and def_card and slot_idx < len(def_card.dice_list) and not target.is_staggered():
            candidate = def_card.dice_list[slot_idx]
            if candidate.dtype in [DiceType.BLOCK, DiceType.EVADE]:
                def_die = candidate
                target.current_die = def_die
                logger.log(f"Triggering Passive Defense: {def_die.dtype.name}", LogLevel.VERBOSE, "OneSided")

        if destroy_def: def_die = None

        if def_die:
            # Passive Clash
            ctx_def = engine._create_roll_context(target, source, def_die, is_disadvantage=adv_def)
            ctx_atk.opponent_ctx = ctx_def
            ctx_def.opponent_ctx = ctx_atk

            val_atk = ctx_atk.final_value
            val_def = ctx_def.final_value

            outcome = ""

            # [FIX] Проверка на взаимную защиту
            is_atk_def = die.dtype in [DiceType.BLOCK, DiceType.EVADE]

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

            logger.log(f"Passive Clash Result: {outcome}", LogLevel.NORMAL, "OneSided")

            report.append({
                "type": "clash",
                "round": f"{round_label} (Passive)",
                "left": {"unit": source.name, "card": card.name, "dice": die.dtype.name, "val": val_atk, "range": "-"},
                "right": {"unit": target.name, "card": def_card.name, "dice": def_die.dtype.name, "val": val_def,
                          "range": "-"},
                "outcome": outcome, "details": detail_logs + ctx_atk.log + ctx_def.log
            })
            att_idx += 1
            continue

        # E. ЧИСТЫЙ УРОН (UNOPPOSED)
        outcome = "Unopposed"
        if is_redirected:
            outcome += " (Redirected)"
        elif destroy_def:
            outcome += " (Speed Break)"

        ATK_TYPES = [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]

        if die.dtype in ATK_TYPES:
            # Атака -> Наносим урон
            logger.log(f"⚔️ Direct Hit! {ctx_atk.final_value} Dmg", LogLevel.NORMAL, "OneSided")
            engine._apply_damage(ctx_atk, None, "hp")

        elif die.dtype == DiceType.EVADE:
            # Уклонение в атаке -> Только запасаем!
            if not hasattr(source, 'stored_dice') or not isinstance(source.stored_dice, list):
                source.stored_dice = []
            source.stored_dice.append(die)
            outcome = "🏃 Evade Stored"
            logger.log("🏃 Evade die stored (Unopposed)", LogLevel.VERBOSE, "OneSided")

        # [FIX] Блок в атаке -> Игнорируется (пропуск)
        elif die.dtype == DiceType.BLOCK:
            outcome = "🛡️ Block (Ignored)"
            logger.log("🛡️ Offensive Block ignored", LogLevel.VERBOSE, "OneSided")

        else:
            outcome += " (Skipped)"

        r_dice_show = "None"
        if destroy_def:
            r_dice_show = "🚫 Broken"
        elif is_redirected:
            r_dice_show = "Busy"

        report.append({
            "type": "onesided",
            "round": f"{round_label} (Hit)",
            "left": {"unit": source.name, "card": card.name, "dice": die.dtype.name, "val": ctx_atk.final_value,
                     "range": "-"},
            "right": {"unit": target.name, "card": "-", "dice": r_dice_show, "val": 0, "range": "-"},
            "outcome": outcome, "details": detail_logs + ctx_atk.log
        })

        att_idx += 1

    if active_counter_die:
        if not hasattr(target, 'stored_dice') or not isinstance(target.stored_dice, list):
            target.stored_dice = []
        target.stored_dice.insert(0, active_counter_die)
        logger.log(f"{target.name} keeps unused counter die", LogLevel.VERBOSE, "OneSided")

    return report