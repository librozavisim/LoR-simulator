from core.logging import logger, LogLevel


def calculate_redirections(atk_team: list, def_team: list):
    """
    Рассчитывает перехваты.
    Правило LoR: Перехват возможен, только если Spd(Atk) > Spd(Def).
    Исключение: Если Def уже целится в Atk (В ТОТ ЖЕ СЛОТ), то это Clash по умолчанию.
    """
    # logger.log("Calculating Redirections...", LogLevel.VERBOSE, "Targeting")

    for def_idx, defender in enumerate(def_team):
        if defender.is_dead(): continue

        for s_def_idx, s_def in enumerate(defender.active_slots):
            if s_def.get('prevent_redirection'): continue
            if s_def.get('stunned'): continue

            def_spd = s_def['speed']

            # Цель защитника (в кого он сам бьет)
            def_target_u_idx = s_def.get('target_unit_idx', -1)
            def_target_s_idx = s_def.get('target_slot_idx', -1)

            valid_interceptors = []

            for atk_u_idx, atk_unit in enumerate(atk_team):
                if atk_unit.is_dead(): continue

                for s_atk_idx, s_atk in enumerate(atk_unit.active_slots):
                    if s_atk.get('is_ally_target'): continue

                    t_u = s_atk.get('target_unit_idx', -1)
                    t_s = s_atk.get('target_slot_idx', -1)

                    # Если этот атакующий бьет в текущего защитника (в текущий слот)
                    if t_u == def_idx and t_s == s_def_idx:
                        # Проверяем "Естественный Клэш" (Def тоже бьет в Atk)
                        is_natural_clash = (def_target_u_idx == atk_u_idx and def_target_s_idx == s_atk_idx)

                        atk_spd = s_atk['speed']

                        can_redirect_equal = False
                        if hasattr(atk_unit, "iter_mechanics"):
                            for mech in atk_unit.iter_mechanics():
                                if mech.can_redirect_on_equal_speed(atk_unit):
                                    can_redirect_equal = True
                                    break

                        if can_redirect_equal:
                            can_redirect = atk_spd >= def_spd
                        else:
                            can_redirect = atk_spd > def_spd

                        if is_natural_clash:
                            # logger.log(f"Natural Clash: {atk_unit.name} <-> {defender.name}", LogLevel.VERBOSE, "Targeting")
                            valid_interceptors.append((s_atk, atk_unit.name))
                        elif can_redirect:
                            # logger.log(f"Redirection Possible: {atk_unit.name} ({atk_spd}) > {defender.name} ({def_spd})", LogLevel.VERBOSE, "Targeting")
                            valid_interceptors.append((s_atk, atk_unit.name))
                        else:
                            # Скорости не хватает и мы не цель защитника -> One Sided
                            # logger.log(f"Redirection Failed: {atk_unit.name} ({atk_spd}) too slow for {defender.name} ({def_spd})", LogLevel.VERBOSE, "Targeting")
                            s_atk['force_clash'] = False
                            s_atk['force_onesided'] = True

            if not valid_interceptors: continue

            # Сортировка перехватчиков (кто быстрее/агрессивнее, тот и забирает клэш)
            def sort_key(item):
                slot, _ = item
                aggro = 1000 if slot.get('is_aggro') else 0
                return aggro + slot['speed']

            valid_interceptors.sort(key=sort_key, reverse=True)

            best_match_slot, best_match_name = valid_interceptors[0]

            # Применяем результаты
            for slot, name in valid_interceptors:
                if slot is best_match_slot:
                    slot['force_clash'] = True
                    slot['force_onesided'] = False
                    logger.log(f"⚔️ Clash Confirmed: {name} intercepts {defender.name} (Slot {s_def_idx})",
                               LogLevel.VERBOSE, "Targeting")
                else:
                    slot['force_clash'] = False
                    slot['force_onesided'] = True
                    logger.log(f"🏹 Forced One-Sided: {name} vs {defender.name} (Outsped by ally)", LogLevel.VERBOSE,
                               "Targeting")