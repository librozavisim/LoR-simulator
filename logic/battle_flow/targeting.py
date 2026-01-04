def calculate_redirections(atk_team: list, def_team: list):
    """
    Рассчитывает перехваты.
    Правило LoR: Перехват возможен, только если Spd(Atk) > Spd(Def).
    Исключение: Если Def уже целится в Atk, то это Clash по умолчанию.
    """
    for def_idx, defender in enumerate(def_team):
        if defender.is_dead(): continue

        for s_def_idx, s_def in enumerate(defender.active_slots):
            if s_def.get('prevent_redirection'): continue
            if s_def.get('stunned'): continue

            def_spd = s_def['speed']

            # Цель защитника (в кого он сам бьет)
            def_target_u_idx = s_def.get('target_unit_idx', -1)
            # def_target_s_idx = s_def.get('target_slot_idx', -1)

            # Кандидаты на перехват
            valid_interceptors = []

            # Проходим по всем атакующим
            for atk_u_idx, atk_unit in enumerate(atk_team):
                if atk_unit.is_dead(): continue

                for s_atk_idx, s_atk in enumerate(atk_unit.active_slots):

                    if s_atk.get('is_ally_target'): continue
                    # Проверяем, бьет ли он в этот слот защитника
                    t_u = s_atk.get('target_unit_idx', -1)
                    t_s = s_atk.get('target_slot_idx', -1)

                    if t_u == def_idx and t_s == s_def_idx:
                        # Условие 1: Это "Естественный Clash" (Враг и так бьет в меня)?
                        is_natural_clash = (def_target_u_idx == atk_u_idx)

                        # Условие 2: Скорость атакующего > Скорости защитника
                        atk_spd = s_atk['speed']

                        has_athletic = ("athletic" in atk_unit.talents) or ("athletic" in atk_unit.passives)

                        if has_athletic:
                            # С талантом: строго больше ИЛИ равно
                            can_redirect = atk_spd >= def_spd
                        else:
                            # Без таланта: строго больше
                            can_redirect = atk_spd > def_spd

                        # Если это естественный бой ИЛИ возможен перехват
                        if is_natural_clash or can_redirect:
                            valid_interceptors.append(s_atk)
                        else:
                            # Если скорости не хватает и это не взаимная атака ->
                            # Атакующий НЕ МОЖЕТ вызвать Clash. Он будет бить One-Sided.
                            s_atk['force_clash'] = False
                            s_atk['force_onesided'] = True

            if not valid_interceptors: continue

            # Теперь выбираем победителя среди валидных кандидатов
            # Приоритет: 1. Галочка Aggro, 2. Скорость
            def sort_key(slot):
                aggro = 1000 if slot.get('is_aggro') else 0
                return aggro + slot['speed']

            valid_interceptors.sort(key=sort_key, reverse=True)

            best_match = valid_interceptors[0]

            for s in valid_interceptors:
                if s is best_match:
                    s['force_clash'] = True
                    s['force_onesided'] = False
                else:
                    s['force_clash'] = False
                    s['force_onesided'] = True