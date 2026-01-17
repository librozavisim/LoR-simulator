from logic.clash import ClashSystem


def precalculate_interactions(team_left: list, team_right: list):
    """
    Финальная версия с визуализацией сломанных кубиков (Speed Break).
    """
    ClashSystem.calculate_redirections(team_left, team_right)
    ClashSystem.calculate_redirections(team_right, team_left)

    def update_ui_status(my_team, enemy_team):
        for my_idx, me in enumerate(my_team):
            for my_slot_idx, my_slot in enumerate(me.active_slots):

                if my_slot.get('stunned'):
                    my_slot['ui_status'] = {"text": "ОГЛУШЕН", "icon": "❌", "color": "gray"}
                    continue

                # Данные о МОЕЙ цели
                t_u_idx = my_slot.get('target_unit_idx', -1)
                t_s_idx = my_slot.get('target_slot_idx', -1)
                is_friendly = my_slot.get('is_ally_target', False)
                target_team_list = my_team if is_friendly else enemy_team

                # --- 1. ПРОВЕРКА: ПЕРЕХВАТИЛИ ЛИ МЕНЯ? ---
                intercepted_by = None
                if not is_friendly:
                    for e_idx, enemy in enumerate(enemy_team):
                        if enemy.is_dead(): continue
                        for e_s_idx, e_slot in enumerate(enemy.active_slots):
                            if e_slot.get('force_clash'):
                                # Враг перехватывает именно этот слот
                                if e_slot.get('target_unit_idx') == my_idx and \
                                        e_slot.get('target_slot_idx') == my_slot_idx:

                                    # Если я тоже целюсь в него в этот слот - это Взаимно, не перехват
                                    if t_u_idx == e_idx and t_s_idx == e_s_idx:
                                        continue

                                    intercepted_by = (enemy, e_slot, e_s_idx)
                                    break
                        if intercepted_by: break

                if intercepted_by:
                    enemy, e_slot, e_s_idx = intercepted_by

                    # === ПРОВЕРКА: Ломает ли враг меня (даже пустым слотом с талантом) ===
                    is_broken = False

                    spd_diff = e_slot['speed'] - my_slot['speed']
                    if spd_diff >= 8:
                        # Условия поломки:
                        # 1. Галочка (Intent) у врага включена (по умолчанию True)
                        e_intent = e_slot.get('destroy_on_speed', True)

                        # 2. У врага есть карта ИЛИ Талант Behavior Study
                        e_has_card = e_slot.get('card') is not None
                        e_has_talent = "behavior_study" in enemy.talents  # Упрощенная проверка для UI

                        if e_intent and (e_has_card or e_has_talent):
                            is_broken = True

                    if is_broken:
                        my_slot['ui_status'] = {
                            "text": f"🚫 BROKEN vs {enemy.name} [S{e_s_idx + 1}] | Speed Gap {spd_diff}",
                            "icon": "💥",
                            "color": "red"
                        }
                    else:
                        my_slot['ui_status'] = {
                            "text": f"CLASH vs {enemy.name} [S{e_s_idx + 1}] | Перехвачен ({my_slot['speed']} < {e_slot['speed']})",
                            "icon": "⚠️",
                            "color": "orange"
                        }
                    continue

                # --- ДАЛЕЕ СТАНДАРТНАЯ ЛОГИКА (Если не перехвачен) ---
                if t_u_idx == -1 or t_u_idx >= len(target_team_list):
                    my_slot['ui_status'] = {"text": "НЕТ ЦЕЛИ", "icon": "⛔", "color": "gray"}
                    continue

                target_unit = target_team_list[t_u_idx]
                if target_unit.is_dead():
                    my_slot['ui_status'] = {"text": "ЦЕЛЬ МЕРТВА", "icon": "💀", "color": "gray"}
                    continue

                tgt_slot_label = "?"
                target_slot = None
                tgt_spd = 0

                if t_s_idx != -1 and t_s_idx < len(target_unit.active_slots):
                    target_slot = target_unit.active_slots[t_s_idx]
                    tgt_spd = target_slot['speed']
                    tgt_slot_label = f"S{t_s_idx + 1}"

                if is_friendly:
                    my_slot['ui_status'] = {"text": f"BUFF -> {target_unit.name}", "icon": "✨", "color": "green"}
                    continue

                # === ПРОВЕРКА: ЛОМАЮ ЛИ Я ВРАГА? ===
                # Это может произойти и в One Sided, и во взаимном Clash
                # Условия: Моя скорость > Врага на 8, Галочка Break, Карта или Талант

                i_break_enemy = False
                if target_slot:
                    my_diff = my_slot['speed'] - tgt_spd
                    if my_diff >= 8:
                        my_intent = my_slot.get('destroy_on_speed', True)
                        my_has_card = my_slot.get('card') is not None
                        my_has_talent = "behavior_study" in me.talents

                        if my_intent and (my_has_card or my_has_talent):
                            i_break_enemy = True

                # === ОПРЕДЕЛЕНИЕ СТАТУСА ===
                is_mutual = False
                if target_slot:
                    if target_slot.get('target_unit_idx') == my_idx and \
                            target_slot.get('target_slot_idx') == my_slot_idx:
                        is_mutual = True

                # Приоритет отображения:
                # 1. Если я ломаю врага (это круто) -> SPEED BREAK
                # 2. Если я проигрываю взаимный клэш и меня ломают -> BROKEN
                # 3. Обычный Clash / One Sided

                enemy_breaks_me_mutual = False
                if is_mutual:
                    # Проверяем, не ломает ли он меня в ответ (взаимный клэш)
                    diff_rev = tgt_spd - my_slot['speed']
                    if diff_rev >= 8:
                        e_intent = target_slot.get('destroy_on_speed', True)
                        e_has = target_slot.get('card') or ("behavior_study" in target_unit.talents)
                        if e_intent and e_has:
                            enemy_breaks_me_mutual = True

                if i_break_enemy:
                    my_slot['ui_status'] = {
                        "text": f"✨ SPEED BREAK -> {target_unit.name} | Уничтожение ({my_slot['speed']} >> {tgt_spd})",
                        "icon": "⚡",
                        "color": "green"
                    }
                    # Если у меня нет карты, но я ломаю талантом - это валидное действие
                    continue

                    # Если нет карты и я НЕ ломаю врага -> я ничего не делаю
                if not my_slot.get('card'):
                    my_slot['ui_status'] = {"text": "НЕТ КАРТЫ", "icon": "⛔", "color": "gray"}
                    continue

                if enemy_breaks_me_mutual:
                    my_slot['ui_status'] = {
                        "text": f"🚫 BROKEN vs {target_unit.name} | Взаимно, он быстрее",
                        "icon": "💥",
                        "color": "red"
                    }

                elif my_slot.get('force_onesided'):
                    my_slot['ui_status'] = {
                        "text": f"ONE SIDED (Провал) -> {target_unit.name} | Слаб",
                        "icon": "🐌",
                        "color": "orange"
                    }

                elif my_slot.get('force_clash'):
                    # Я кого-то перехватил
                    my_slot['ui_status'] = {
                        "text": f"CLASH vs {target_unit.name} [{tgt_slot_label}] | Перехват!",
                        "icon": "⚡",
                        "color": "red"
                    }

                elif is_mutual:
                    # Взаимная атака (без перехвата, просто совпали слоты)
                    my_slot['ui_status'] = {
                        "text": f"CLASH vs {target_unit.name} [{tgt_slot_label}] | Взаимно",
                        "icon": "⚔️",
                        "color": "red"
                    }

                else:
                    reason = "Свободно"
                    if target_slot and target_slot.get('stunned'):
                        reason = "Враг оглушен"
                    elif target_slot:
                        reason = "Враг занят/игнор"

                    my_slot['ui_status'] = {
                        "text": f"ATK -> {target_unit.name} [{tgt_slot_label}] | {reason}",
                        "icon": "🏹",
                        "color": "blue"
                    }

    update_ui_status(team_left, team_right)
    update_ui_status(team_right, team_left)