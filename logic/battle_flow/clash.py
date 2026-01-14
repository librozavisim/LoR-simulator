from core.enums import DiceType
from logic.battle_flow.speed import calculate_speed_advantage


def process_clash(engine, attacker, defender, round_label, is_left, spd_a, spd_d, intent_a=True, intent_d=True):
    report = []
    ac = attacker.current_card
    dc = defender.current_card

    # Скрипты On Use
    on_use_logs = []
    engine._process_card_self_scripts("on_use", attacker, defender, custom_log_list=on_use_logs)
    engine._process_card_self_scripts("on_use", defender, attacker, custom_log_list=on_use_logs)

    # Расчет преимущества скорости
    adv_a, adv_d, destroy_a, destroy_d = calculate_speed_advantage(spd_a, spd_d, intent_a, intent_d)

    # Проверка иммунитета к уничтожению кубиков
    prevent_dest_a = False
    if hasattr(attacker, "iter_mechanics"):
        for mech in attacker.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(attacker):
                prevent_dest_a = True
                break

    if destroy_d and prevent_dest_a:
        destroy_d = False
        adv_a = True

    prevent_dest_d = False
    if hasattr(defender, "iter_mechanics"):
        for mech in defender.iter_mechanics():
            if mech.prevents_dice_destruction_by_speed(defender):
                prevent_dest_d = True
                break

    if destroy_a and prevent_dest_d:
        destroy_a = False
        adv_d = True

    queue_a = list(ac.dice_list)
    queue_d = list(dc.dice_list)

    # Переменные для хранения "ресайкнутых" кубиков.
    # Храним кортеж (Die, is_from_storage)
    active_counter_a = None
    active_counter_d = None

    def resolve_slot_die(unit, queue, idx, is_broken, active_counter_tuple):
        # 1. Приоритет: Активный ресайкнутый кубик
        if active_counter_tuple:
            return active_counter_tuple[0], active_counter_tuple[1]

        # 2. Кубик карты
        card_die = None
        if idx < len(queue):
            card_die = queue[idx]
            if is_broken:
                is_saved = False
                if hasattr(unit, "iter_mechanics"):
                    for mech in unit.iter_mechanics():
                        if mech.prevents_specific_die_destruction(unit, card_die):
                            is_saved = True;
                            break
                if not is_saved:
                    card_die = None

        # 3. Запас (Stored/Counter)
        if not card_die:
            if hasattr(unit, 'stored_dice') and isinstance(unit.stored_dice, list) and unit.stored_dice:
                if unit.is_staggered():
                    can_use = False
                    if hasattr(unit, "iter_mechanics"):
                        for mech in unit.iter_mechanics():
                            if mech.can_use_counter_die_while_staggered(unit):
                                can_use = True;
                                break
                    if not can_use: return None, False
                return unit.stored_dice.pop(0), True

            if unit.counter_dice:
                if unit.is_staggered():
                    can_use = False
                    if hasattr(unit, "iter_mechanics"):
                        for mech in unit.iter_mechanics():
                            if mech.can_use_counter_die_while_staggered(unit):
                                can_use = True;
                                break
                    if not can_use: return None, False
                return unit.counter_dice.pop(0), True

            return None, False

        return card_die, False

    idx_a = 0
    idx_d = 0
    iteration = 0
    max_iterations = 25

    while (idx_a < len(queue_a) or idx_d < len(
            queue_d) or active_counter_a or active_counter_d) and iteration < max_iterations:
        iteration += 1

        if attacker.is_dead() or defender.is_dead(): break

        is_break_a = destroy_a if idx_a < len(queue_a) else False
        is_break_d = destroy_d if idx_d < len(queue_d) else False

        die_a, src_a = resolve_slot_die(attacker, queue_a, idx_a, is_break_a, active_counter_a)
        die_d, src_d = resolve_slot_die(defender, queue_d, idx_d, is_break_d, active_counter_d)

        # Выход если оба пусты
        if not die_a and not die_d:
            if idx_a < len(queue_a): idx_a += 1
            if idx_d < len(queue_d): idx_d += 1
            if idx_a >= len(queue_a) and idx_d >= len(queue_d): break
            continue

        if die_a: attacker.current_die = die_a
        if die_d: defender.current_die = die_d

        type_a = die_a.dtype if die_a else None
        type_d = die_d.dtype if die_d else None

        is_atk_a = type_a in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]
        is_evade_a = type_a == DiceType.EVADE
        is_block_a = type_a == DiceType.BLOCK

        is_atk_d = type_d in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]
        is_evade_d = type_d == DiceType.EVADE
        is_block_d = type_d == DiceType.BLOCK

        ctx_a = engine._create_roll_context(attacker, defender, die_a, is_disadvantage=adv_a) if die_a else None
        ctx_d = engine._create_roll_context(defender, attacker, die_d, is_disadvantage=adv_d) if die_d else None

        val_a = ctx_a.final_value if ctx_a else 0
        val_d = ctx_d.final_value if ctx_d else 0

        if ctx_a and ctx_d:
            ctx_a.opponent_ctx = ctx_d
            ctx_d.opponent_ctx = ctx_a

        outcome = ""
        detail_logs = []
        if iteration == 1 and on_use_logs: detail_logs.extend(on_use_logs)
        if ctx_a: detail_logs.extend(ctx_a.log)
        if ctx_d: detail_logs.extend(ctx_d.log)

        # --- UPDATE FUNCTIONS ---

        def consume_die_a_fn():
            nonlocal active_counter_a, idx_a
            if active_counter_a:
                active_counter_a = None
            elif not src_a:
                idx_a += 1

        def consume_die_d_fn():
            nonlocal active_counter_d, idx_d
            if active_counter_d:
                active_counter_d = None
            elif not src_d:
                idx_d += 1

        def recycle_die_a_fn():
            nonlocal active_counter_a, idx_a
            if not active_counter_a:
                active_counter_a = (die_a, src_a)
                if not src_a: idx_a += 1

        def recycle_die_d_fn():
            nonlocal active_counter_d, idx_d
            if not active_counter_d:
                active_counter_d = (die_d, src_d)
                if not src_d: idx_d += 1

        # --- RESOLVE ---

        # 1. Broken / Empty
        if not die_a and die_d:
            # [FIX] Если у защитника Уклонение/Блок, а врага нет -> Прерываем (сохраняем)
            if is_evade_d or is_block_d:
                break
            outcome = f"🚫 {attacker.name} Broken"
            if is_atk_d: engine._apply_damage(ctx_d, None, "hp")
            consume_die_a_fn()
            consume_die_d_fn()

        elif die_a and not die_d:
            # [FIX] Если у атакующего Уклонение/Блок, а врага нет -> Прерываем (сохраняем)
            if is_evade_a or is_block_a:
                break
            outcome = f"🚫 {defender.name} Broken"
            if is_atk_a: engine._apply_damage(ctx_a, None, "hp")
            consume_die_a_fn()
            consume_die_d_fn()

        # 2. Defensive vs Defensive
        elif (is_evade_a or is_block_a) and (is_evade_d or is_block_d):
            outcome = "🛡️ Defensive Clash (Both Spent)"
            consume_die_a_fn()
            consume_die_d_fn()

        # 3. Clash
        else:
            if val_a > val_d:
                engine._handle_clash_win(ctx_a)
                engine._handle_clash_lose(ctx_d)

                if is_atk_a and is_atk_d:
                    outcome = f"🏆 {attacker.name} Win (Hit)"
                    engine._resolve_clash_interaction(ctx_a, ctx_d, val_a - val_d)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_atk_a and is_evade_d:
                    outcome = f"💥 Evade Failed"
                    engine._resolve_clash_interaction(ctx_a, ctx_d, val_a)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_evade_a and is_atk_d:
                    outcome = f"🏃 {attacker.name} Evades! (Recycle)"
                    rec = attacker.restore_stagger(val_a)
                    detail_logs.append(f"🛡️ +{rec} Stagger")
                    recycle_die_a_fn()
                    consume_die_d_fn()

                elif is_atk_a and is_block_d:
                    outcome = f"🔨 Block Broken"
                    defender.take_stagger_damage(val_a - val_d)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_block_a and is_atk_d:
                    outcome = f"🛡️ Blocked"
                    attacker.restore_stagger(val_a - val_d)
                    consume_die_a_fn();
                    consume_die_d_fn()

            elif val_d > val_a:
                engine._handle_clash_win(ctx_d)
                engine._handle_clash_lose(ctx_a)

                if is_atk_d and is_atk_a:
                    outcome = f"🏆 {defender.name} Win (Hit)"
                    engine._resolve_clash_interaction(ctx_d, ctx_a, val_d - val_a)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_atk_d and is_evade_a:
                    outcome = f"💥 Evade Failed"
                    engine._resolve_clash_interaction(ctx_d, ctx_a, val_d)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_evade_d and is_atk_a:
                    outcome = f"🏃 {defender.name} Evades! (Recycle)"
                    rec = defender.restore_stagger(val_d)
                    detail_logs.append(f"🛡️ +{rec} Stagger")
                    recycle_die_d_fn()
                    consume_die_a_fn()

                elif is_atk_d and is_block_a:
                    outcome = f"🔨 Block Broken"
                    attacker.take_stagger_damage(val_d - val_a)
                    consume_die_a_fn();
                    consume_die_d_fn()

                elif is_block_d and is_atk_a:
                    outcome = f"🛡️ Blocked"
                    defender.restore_stagger(val_d - val_a)
                    consume_die_a_fn();
                    consume_die_d_fn()

            else:
                outcome = "🤝 Draw"
                engine._handle_clash_draw(ctx_a)
                engine._handle_clash_draw(ctx_d)
                consume_die_a_fn();
                consume_die_d_fn()

        l_lbl = die_a.dtype.name if die_a else "Broken"
        r_lbl = die_d.dtype.name if die_d else "Broken"
        if src_a: l_lbl += " (C)"
        if src_d: r_lbl += " (C)"
        l_rng = f"{die_a.min_val}-{die_a.max_val}" if die_a else "-"
        r_rng = f"{die_d.min_val}-{die_d.max_val}" if die_d else "-"

        report.append({
            "type": "clash",
            "round": f"{round_label} ({iteration})",
            "left": {"unit": attacker.name if is_left else defender.name,
                     "card": ac.name if is_left else dc.name,
                     "dice": l_lbl if is_left else r_lbl, "val": val_a if is_left else val_d,
                     "range": l_rng if is_left else r_rng},
            "right": {"unit": defender.name if is_left else attacker.name,
                      "card": dc.name if is_left else ac.name,
                      "dice": r_lbl if is_left else l_lbl, "val": val_d if is_left else val_a,
                      "range": r_rng if is_left else l_rng},
            "outcome": outcome, "details": detail_logs
        })

    # === СОХРАНЕНИЕ ===

    def store_remaining_dice(unit, queue, idx, active_cnt_tuple, log_list):
        if not hasattr(unit, 'stored_dice') or not isinstance(unit.stored_dice, list):
            unit.stored_dice = []

        # 1. Активный ресайкнутый кубик
        if active_cnt_tuple:
            die, is_from_storage = active_cnt_tuple
            if die.dtype == DiceType.EVADE:
                # [FIX] Сохраняем ТОЛЬКО если он был Stored/Counter (src=True).
                # Если он был с карты (src=False) и был активирован (попал в active_cnt_tuple),
                # значит он "потратился" (хоть и выиграл), поэтому в конце сцены сгорает.
                if is_from_storage:
                    unit.stored_dice.append(die)
                    log_list.append({"type": "info", "outcome": f"🛡️ {unit.name} Kept Counter Evade", "details": []})

        # 2. Оставшиеся (неиспользованные) кубики в очереди
        # Эти кубики даже не вступали в бой (мы сделали break раньше), поэтому они сохраняются.
        while idx < len(queue):
            die = queue[idx]
            if die.dtype == DiceType.EVADE:
                unit.stored_dice.append(die)
                log_list.append({
                    "type": "info",
                    "outcome": f"🛡️ {unit.name} Stored Evade Die",
                    "details": [f"Die {die.min_val}-{die.max_val} saved."]
                })
            idx += 1

    store_remaining_dice(attacker, queue_a, idx_a, active_counter_a, report)
    store_remaining_dice(defender, queue_d, idx_d, active_counter_d, report)

    return report