import random
from logic.battle_flow.targeting import calculate_redirections
from logic.battle_flow.priorities import get_action_priority


def prepare_turn(engine, team_left: list, team_right: list):
    """
    Фаза 1: Сбор всех запланированных действий (Actions) и сортировка по скорости/приоритету.
    """
    engine.logs = []
    report = []
    all_units = team_left + team_right

    # Рассчитываем перехваты для обеих команд
    calculate_redirections(team_left, team_right)
    calculate_redirections(team_right, team_left)

    # --- A. Триггеры начала боя (On Combat Start) ---
    for u in all_units:
        opponents = team_right if u in team_left else team_left
        opp_ref = next((e for e in opponents if not e.is_dead()), None)
        my_allies = team_left if u in team_left else team_right

        engine._trigger_unit_event("on_round_start", unit=u, log_func=engine.log,
                                   opponent=opp_ref, enemies=opponents, allies=my_allies)

        if engine.logs:
            report.append({"round": "Start", "rolls": "Events", "details": " | ".join(engine.logs)})
        engine.logs = []

    # --- B. Сбор действий ---
    actions = []

    def collect_actions(source_team, target_team, is_left_side):
        for u_idx, unit in enumerate(source_team):
            if unit.is_dead(): continue
            for s_idx, slot in enumerate(unit.active_slots):
                card = slot.get('card')
                if card and not slot.get('stunned'):
                    base_prio = get_action_priority(card)
                    # Левая сторона получает микро-бонус приоритета при прочих равных (convention)
                    if base_prio >= 4000 and is_left_side: base_prio += 500
                    score = base_prio + slot['speed'] + random.random()

                    # ВЫБОР ЦЕЛИ
                    t_u_idx = slot.get('target_unit_idx', -1)
                    target_unit = None

                    if slot.get('is_ally_target'):
                        if t_u_idx != -1 and t_u_idx < len(source_team):
                            target_unit = source_team[t_u_idx]
                    else:
                        if t_u_idx != -1 and t_u_idx < len(target_team):
                            target_unit = target_team[t_u_idx]

                    actions.append({
                        'source': unit,
                        'source_idx': s_idx,
                        'target_unit': target_unit,
                        'target_slot_idx': slot.get('target_slot_idx', -1),
                        'slot_data': slot,
                        'score': score,
                        'is_left': is_left_side,
                        'card_type': str(card.card_type).lower(),
                        'opposing_team': target_team
                    })

    collect_actions(team_left, team_right, True)
    collect_actions(team_right, team_left, False)

    actions.sort(key=lambda x: x['score'], reverse=True)

    return report, actions


def finalize_turn(engine, all_units: list):
    """
    Фаза 3: Завершение хода (Events On Combat End).
    """
    engine.logs = []
    report = []

    if engine.logs:
        report.append({"round": "End", "rolls": "Events", "details": " | ".join(engine.logs)})

    return report