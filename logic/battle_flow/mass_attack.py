import random
from core.enums import CardType
from core.logging import logger, LogLevel


def process_mass_attack(engine, action, opposing_team, round_label):
    """
    Обрабатывает массовую атаку (Суммарную или Индивидуальную).
    Массовая атака бьет ВСЕХ врагов.
    """
    source = action['source']
    card = source.current_card

    is_summation = (card.card_type == CardType.MASS_SUMMATION.value)

    report = []

    # 1. Логируем начало атаки
    atk_type_str = "Summation" if is_summation else "Individual"
    logger.log(f"💥 {source.name} uses Mass Attack: {card.name} ({atk_type_str})", LogLevel.NORMAL, "MassAtk")

    # 2. Перебираем всех живых врагов
    for target in opposing_team:
        if target.is_dead(): continue

        # Выбираем случайный слот врага для атаки (по правилам LoR)
        target_slot = None
        target_dice_list = []

        if not target.is_staggered() and target.active_slots:
            valid_slots = [s for s in target.active_slots if s.get('card')]
            if valid_slots:
                target_slot = random.choice(valid_slots)
                if target_slot.get('card'):
                    target_dice_list = target_slot['card'].dice_list
                    logger.log(f"Targeting {target.name} (Defending with {target_slot['card'].name})", LogLevel.VERBOSE,
                               "MassAtk")
        else:
            logger.log(f"Targeting {target.name} (No defense/Staggered)", LogLevel.VERBOSE, "MassAtk")

        # === ЛОГИКА MASS-SUMMATION (Сумма на Сумму) ===
        if is_summation:
            # Считаем сумму кубиков Атакующего
            atk_sum = 0
            atk_rolls = []
            for d in card.dice_list:
                ctx = engine._create_roll_context(source, target, d)
                atk_sum += ctx.final_value
                atk_rolls.append(str(ctx.final_value))

            # Считаем сумму кубиков Защитника
            def_sum = 0
            def_rolls = []
            for d in target_dice_list:
                ctx = engine._create_roll_context(target, source, d)
                def_sum += ctx.final_value
                def_rolls.append(str(ctx.final_value))

            outcome = ""
            details = []

            logger.log(f"∑ Clash: {source.name}({atk_sum}) vs {target.name}({def_sum})", LogLevel.VERBOSE, "MassAtk")

            # Сравнение
            if atk_sum > def_sum:
                outcome = f"🎯 Hit! ({atk_sum} > {def_sum})"

                # Уничтожаем карту врага
                if target_slot:
                    target_slot['card'] = None  # Destroy page
                    details.append(f"🚫 {target.name}'s page destroyed!")
                    logger.log(f"🚫 {target.name}'s page destroyed by Mass Summation", LogLevel.NORMAL, "MassAtk")

                # Наносим урон каждого кубика
                for d in card.dice_list:
                    ctx_dmg = engine._create_roll_context(source, target, d)
                    engine._apply_damage(ctx_dmg, None, "hp")
                    details.extend(ctx_dmg.log)
            else:
                outcome = f"🛡️ Blocked ({def_sum} >= {atk_sum})"
                details.append(f"{target.name} withstood the attack.")
                logger.log(f"🛡️ {target.name} blocked Mass Attack", LogLevel.NORMAL, "MassAtk")

            # Добавляем в отчет
            report.append({
                "type": "clash",
                "round": f"{round_label} (Mass)",
                "left": {"unit": source.name, "card": "MASS SUM", "dice": "Sum", "val": atk_sum,
                         "range": f"Rolls: {','.join(atk_rolls)}"},
                "right": {"unit": target.name, "card": "Defense", "dice": "Sum", "val": def_sum,
                          "range": f"Rolls: {','.join(def_rolls)}"},
                "outcome": outcome, "details": details
            })

        # === ЛОГИКА MASS-INDIVIDUAL (Кубик на Кубик) ===
        else:
            num_checks = len(card.dice_list)

            for i in range(num_checks):
                die_atk = card.dice_list[i]
                die_def = target_dice_list[i] if i < len(target_dice_list) else None

                ctx_atk = engine._create_roll_context(source, target, die_atk)
                val_atk = ctx_atk.final_value

                val_def = 0
                ctx_def = None

                if die_def:
                    ctx_def = engine._create_roll_context(target, source, die_def)
                    val_def = ctx_def.final_value

                details = []
                outcome = ""

                logger.log(f"Indiv Clash #{i + 1}: {val_atk} vs {val_def}", LogLevel.VERBOSE, "MassAtk")

                if val_atk > val_def:
                    outcome = "🎯 Hit"
                    if target_slot and i < len(target_slot['card'].dice_list):
                        details.append(f"🚫 {target.name}'s Die #{i + 1} destroyed")
                        logger.log(f"🚫 {target.name}'s Die #{i + 1} destroyed", LogLevel.NORMAL, "MassAtk")

                    engine._apply_damage(ctx_atk, None, "hp")
                    details.extend(ctx_atk.log)
                else:
                    outcome = "🛡️ Blocked"

                r_dice_name = die_def.dtype.name if die_def else "None"
                report.append({
                    "type": "clash",
                    "round": f"{round_label} (M-Indiv {i + 1})",
                    "left": {"unit": source.name, "card": "Mass", "dice": die_atk.dtype.name, "val": val_atk,
                             "range": "-"},
                    "right": {"unit": target.name, "card": "-", "dice": r_dice_name, "val": val_def, "range": "-"},
                    "outcome": outcome, "details": details
                })

    return report