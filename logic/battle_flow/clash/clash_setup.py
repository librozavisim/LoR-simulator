from core.logging import logger, LogLevel
from logic.battle_flow.speed import calculate_speed_advantage
from logic.battle_flow.clash.clash_utils import check_destruction_immunity


def setup_clash_parameters(engine, attacker, defender, spd_a, spd_d, intent_a, intent_d):
    """
    Выполняет скрипты On Use и рассчитывает параметры скорости и разрушения кубиков.
    Возвращает: (adv_a, adv_d, destroy_a, destroy_d, on_use_logs)
    """
    # 1. Скрипты On Use
    on_use_logs = []
    engine._process_card_self_scripts("on_use", attacker, defender, custom_log_list=on_use_logs)
    engine._process_card_self_scripts("on_use", defender, attacker, custom_log_list=on_use_logs)

    for log in on_use_logs:
        logger.log(f"On Use: {log}", LogLevel.VERBOSE, "Script")

    # 2. Расчет преимущества скорости
    adv_a, adv_d, destroy_a, destroy_d = calculate_speed_advantage(spd_a, spd_d, intent_a, intent_d)

    if destroy_a or destroy_d:
        logger.log(f"Speed Break: {attacker.name} destroy={destroy_a}, {defender.name} destroy={destroy_d}",
                   LogLevel.VERBOSE, "Clash")

    # 3. Проверка иммунитета к уничтожению
    if destroy_d and check_destruction_immunity(attacker):
        logger.log(f"{defender.name}'s dice saved by immunity", LogLevel.VERBOSE, "Clash")
        destroy_d = False
        adv_a = True

    if destroy_a and check_destruction_immunity(defender):
        logger.log(f"{attacker.name}'s dice saved by immunity", LogLevel.VERBOSE, "Clash")
        destroy_a = False
        adv_d = True

    return adv_a, adv_d, destroy_a, destroy_d, on_use_logs