from core.enums import DiceType
from logic.battle_flow.speed import calculate_speed_advantage


def process_onesided(engine, source, target, round_label, spd_atk, spd_d, intent_atk=True, is_redirected=False):
    report = []
    card = source.current_card
    def_card = target.current_card

    # Расчет преимущества скорости
    adv_atk, adv_def, _, destroy_def = calculate_speed_advantage(spd_atk, spd_d, intent_atk, True)

    # 1. Break Check (Empty Slot Break)
    defender_breaks_attacker = False
    if not def_card:
        if spd_d - spd_atk >= 8:
            if hasattr(target, "iter_mechanics"):
                for mech in target.iter_mechanics():
                    if hasattr(mech, "can_break_empty_slot") and mech.can_break_empty_slot(target):
                        defender_breaks_attacker = True
                        break

    # 2. Prevent Destruction (Passive)
    prevent_dest = False
    if hasattr(source, "iter_mechanics"):
        for mech in source.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(source):
                prevent_dest = True
                break

    if destroy_def and prevent_dest:
        destroy_def = False
        adv_atk = True

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
                            can_use = True;
                            break
                if not can_use: return None
            return unit.stored_dice.pop(0)

        # 2. Counter Dice
        if unit.counter_dice:
            if unit.is_staggered():
                can_use = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.can_use_counter_die_while_staggered(unit):
                            can_use = True;
                            break
                if not can_use: return None
            return unit.counter_dice.pop(0)
        return None

    max_iter = 20
    cur_iter = 0

    while att_idx < len(attacker_queue) and cur_iter < max_iter:
        cur_iter += 1
        die = attacker_queue[att_idx]

        if source.is_dead() or target.is_dead() or source.is_staggered(): break
        source.current_die = die

        detail_logs = []
        if att_idx == 0 and on_use_logs: detail_logs.extend(on_use_logs)

        # A. Break Check
        if defender_breaks_attacker:
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
            engine._apply_damage(ctx_atk, None, "hp")

        elif die.dtype == DiceType.EVADE:
            # Уклонение в атаке -> Только запасаем!
            if not hasattr(source, 'stored_dice') or not isinstance(source.stored_dice, list):
                source.stored_dice = []
            source.stored_dice.append(die)
            outcome = "🏃 Evade Stored"

        # [FIX] Блок в атаке -> Игнорируется (пропуск)
        elif die.dtype == DiceType.BLOCK:
            outcome = "🛡️ Block (Ignored)"
            # Ничего не делаем, не запасаем, не наносим урон

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

    return report