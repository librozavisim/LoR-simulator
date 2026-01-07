import sys
import streamlit as st
from contextlib import contextmanager
from io import StringIO

from core.card import Card
from core.library import Library
from logic.character_changing.augmentations.augmentations import AUGMENTATION_REGISTRY
from logic.clash import ClashSystem
from logic.character_changing.passives import PASSIVE_REGISTRY
from logic.character_changing.talents import TALENT_REGISTRY
from logic.statuses.status_manager import StatusManager


@contextmanager
def capture_output():
    new_out = StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out


def get_teams():
    """Вспомогательная функция для получения команд из сессии."""
    return st.session_state.get('team_left', []), st.session_state.get('team_right', [])


def set_cooldowns(u):
    if not u.memory.get("battle_initialized"):
        u.memory["battle_initialized"] = True
        u.card_cooldowns = {}

        if getattr(u, 'deck', None):
            for card_id in u.deck:
                card = Library.get_card(card_id)
                if card:
                    initial_cd = max(0, card.tier - 1)
                    if initial_cd > 0:
                        u.card_cooldowns[card_id] = initial_cd

        # === [ИЗМЕНЕНИЕ] Запуск on_combat_start только один раз в начале боя ===
        # Находим врагов и союзников для контекста
        l_team, r_team = get_teams()
        opponents = r_team if u in l_team else l_team
        my_allies = l_team if u in l_team else r_team

        # Для простоты логов (в консоль или лог боя)
        # Если нужно вывести в UI, можно сохранить в st.session_state['turn_message'] или аналог
        # Но здесь мы просто инициализируем состояние.

        def log_dummy(msg):
            # Можно добавлять в стартовое сообщение, если очень нужно
            pass

        # 1. Passives
        for pid in u.passives:
            if pid in PASSIVE_REGISTRY:
                PASSIVE_REGISTRY[pid].on_combat_start(u, log_dummy, enemies=opponents, allies=my_allies)
        # 2. Talents
        for pid in u.talents:
            if pid in TALENT_REGISTRY:
                TALENT_REGISTRY[pid].on_combat_start(u, log_dummy, enemies=opponents, allies=my_allies)
        # 3. Weapons
        from logic.weapon_definitions import WEAPON_REGISTRY
        if u.weapon_id in WEAPON_REGISTRY:
            wep = WEAPON_REGISTRY[u.weapon_id]
            if wep.passive_id and wep.passive_id in PASSIVE_REGISTRY:
                PASSIVE_REGISTRY[wep.passive_id].on_combat_start(u, log_dummy, enemies=opponents, allies=my_allies)
        for aid in u.augmentations:
            if aid in AUGMENTATION_REGISTRY:
                AUGMENTATION_REGISTRY[aid].on_combat_start(u, log_dummy, enemies=opponents, allies=my_allies)

def roll_phase():
    """
    Фаза броска скорости.
    Инициализирует слоты для всех юнитов в обеих командах.
    """
    l_team, r_team = get_teams()
    all_units = l_team + r_team

    # 1. Пересчет статов и бросок скорости
    for u in all_units:
        u.recalculate_stats()
        set_cooldowns(u)

        if u.is_staggered():
            # Оглушенный юнит получает 1 слот с 0 скорости
            u.active_slots = [{
                'speed': 0, 'card': None,
                'target_unit_idx': -1, 'target_slot_idx': -1,
                'stunned': True, 'is_aggro': False
            }]
        else:
            u.roll_speed_dice()
            # Инициализация полей цели для каждого слота
            for s in u.active_slots:
                s['target_unit_idx'] = -1
                s['target_slot_idx'] = -1
                s['is_aggro'] = False
                s['force_clash'] = False

    # 2. Авто-таргетинг (Auto-Targeting)
    # По умолчанию левые бьют первых живых правых, и наоборот.
    def set_default_targets(source_team, target_team):
        if not target_team: return
        # Индексы живых врагов
        alive_targets = [i for i, t in enumerate(target_team) if not t.is_dead()]

        # Ищем провокаторов
        taunt_targets = [i for i, t in enumerate(target_team) if not t.is_dead() and t.get_status("taunt") > 0]

        # Если есть провокаторы, список целей сужается только до них
        valid_targets = taunt_targets if taunt_targets else alive_targets

        if not valid_targets: return  # Некого бить

        for u in source_team:
            if u.is_dead() or u.is_staggered(): continue
            for slot in u.active_slots:
                # Простое правило: бьем первого живого врага в первый слот
                slot['target_unit_idx'] = valid_targets[0]
                slot['target_slot_idx'] = 0

    set_default_targets(l_team, r_team)
    set_default_targets(r_team, l_team)

    st.session_state['phase'] = 'planning'
    st.session_state['turn_message'] = "🎲 Speed Rolled (Targets Auto-Assigned)"


def step_start():
    """Начало пошагового боя."""
    l_team, r_team = get_teams()
    sys_clash = ClashSystem()

    # Подготовка хода (расчет инициативы, событий начала боя)
    init_logs, actions = sys_clash.prepare_turn(l_team, r_team)

    st.session_state['battle_logs'] = init_logs
    st.session_state['turn_actions'] = actions
    # Множество отыгранных слотов: (unit_name, slot_idx)
    st.session_state['executed_slots'] = set()
    st.session_state['turn_phase'] = 'fighting'
    st.session_state['action_idx'] = 0


def step_next():
    """Выполнение следующего действия в очереди."""
    actions = st.session_state.get('turn_actions', [])
    idx = st.session_state.get('action_idx', 0)

    if idx < len(actions):
        sys_clash = ClashSystem()
        act = actions[idx]
        # Выполняем действие
        logs = sys_clash.execute_single_action(act, st.session_state['executed_slots'])
        st.session_state['battle_logs'].extend(logs)
        st.session_state['action_idx'] += 1

    # Если действия кончились, завершаем раунд
    if st.session_state['action_idx'] >= len(actions):
        step_finish()


def step_finish():
    """Завершение фазы боя."""
    l_team, r_team = get_teams()
    sys_clash = ClashSystem()

    # События конца хода (End of Combat Events)
    end_logs = sys_clash.finalize_turn(l_team + r_team)
    st.session_state['battle_logs'].extend(end_logs)

    finish_round_logic()


def execute_combat_auto():
    """Автоматический расчет всего раунда."""
    l_team, r_team = get_teams()
    sys_clash = ClashSystem()

    with capture_output() as captured:
        logs = sys_clash.resolve_turn(l_team, r_team)

    st.session_state['battle_logs'] = logs
    st.session_state['script_logs'] = captured.getvalue()

    finish_round_logic()


def finish_round_logic():
    """Общая логика завершения раунда (очистка, кулдауны, реген)."""
    l_team, r_team = get_teams()
    all_units = l_team + r_team
    msg = []

    def log_collector(message):
        msg.append(message)

    for u in all_units:
        # Восстановление Stagger, если был оглушен
        if u.active_slots and u.active_slots[0].get('stunned'):
            u.current_stagger = u.max_stagger
            msg.append(f"✨ {u.name} recovered!")

        # Определяем союзников для передачи в таланты
        my_allies = l_team if u in l_team else r_team

        # Пассивки и Таланты (On Round End)
        for pid in u.passives:
            if pid in PASSIVE_REGISTRY:
                PASSIVE_REGISTRY[pid].on_round_end(u, log_collector, allies=my_allies)
        for pid in u.talents:
            if pid in TALENT_REGISTRY:
                TALENT_REGISTRY[pid].on_round_end(u, log_collector, allies=my_allies)
        # Статусы (снижение длительности, эффекты конца хода)
        StatusManager.process_turn_end(u)

        # Кулдауны
        u.tick_cooldowns()

        # Очистка слотов
        u.active_slots = []

    st.session_state['turn_message'] = " ".join(msg) if msg else "Round Complete."
    st.session_state['phase'] = 'roll'
    st.session_state['turn_phase'] = 'done'


def reset_game():
    """Полный сброс состояния боя."""
    l_team, r_team = get_teams()
    all_units = l_team + r_team

    for u in all_units:
        u.recalculate_stats()
        u.current_hp = u.max_hp
        u.current_stagger = u.max_stagger
        u.current_sp = u.max_sp
        u._status_effects = {}
        u.delayed_queue = []
        u.active_slots = []
        set_cooldowns(u)
        u.active_buffs = {}
        u.memory = {}

    st.session_state['battle_logs'] = []
    st.session_state['script_logs'] = ""
    st.session_state['turn_message'] = "Game Reset."
    st.session_state['phase'] = 'roll'


def sync_state_from_widgets(team_left: list, team_right: list):
    """
    Считывает значения из виджетов Streamlit и обновляет объекты юнитов.
    Ключи должны совпадать с теми, что генерируются в simulator_components.py.
    Format ключа: {prefix}_{unit.name}_{type}_{slot_idx}
    """

    def sync_unit(unit, prefix):
        for i, slot in enumerate(unit.active_slots):
            if slot.get('stunned'): continue

            base_key = f"{prefix}_{unit.name}"

            # 1. TARGET (Цель)
            tgt_key = f"{base_key}_tgt_{i}"
            if tgt_key in st.session_state:
                val = st.session_state[tgt_key]
                # val format: "1:1 | Label" OR "None" (где 1:1 это UI индексы)

                if val == "None":
                    slot['target_unit_idx'] = -1
                    slot['target_slot_idx'] = -1
                else:
                    try:
                        # Парсим "1:1 | Name..."
                        parts = val.split('|')[0].strip().split(':')
                        # [FIX] Вычитаем 1 при сохранении в структуру юнита
                        slot['target_unit_idx'] = int(parts[0]) - 1
                        slot['target_slot_idx'] = int(parts[1]) - 1
                    except:
                        pass  # Ошибка парсинга

            # 2. CARD (Карта)
            card_key = f"{base_key}_card_{i}"
            if card_key in st.session_state:
                val = st.session_state[card_key]
                if isinstance(val, Card):
                    slot['card'] = val
                elif val is None:
                    slot['card'] = None

            # 3. AGGRO (Перехват)
            aggro_key = f"{base_key}_aggro_{i}"
            if aggro_key in st.session_state:
                slot['is_aggro'] = st.session_state[aggro_key]

    # Синхронизируем Левую команду (prefix l_i)
    for i, u in enumerate(team_left):
        sync_unit(u, f"l_{i}")

    # Синхронизируем Правую команду (prefix r_i)
    for i, u in enumerate(team_right):
        sync_unit(u, f"r_{i}")


def precalculate_interactions(team_left: list, team_right: list):
    """
    Финальная версия с исправлением ложных перехватов при взаимных атаках.
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
                # Ищем врага, который имеет force_clash на меня
                intercepted_by = None

                # (Только если мы бьем врагов, а не лечим своих)
                if not is_friendly:
                    for e_idx, enemy in enumerate(enemy_team):
                        if enemy.is_dead(): continue
                        for e_s_idx, e_slot in enumerate(enemy.active_slots):
                            # Если враг имеет force_clash И целится в меня
                            if e_slot.get('force_clash'):
                                if e_slot.get('target_unit_idx') == my_idx and \
                                        e_slot.get('target_slot_idx') == my_slot_idx:

                                    # === [FIX] ГЛАВНОЕ ИСПРАВЛЕНИЕ ===
                                    # Если я тоже целюсь в ЭТОГО врага в ЭТОТ слот -> Это ВЗАИМНО.
                                    # Не считаем это перехватом, пропускаем.
                                    if t_u_idx == e_idx and t_s_idx == e_s_idx:
                                        continue
                                        # =================================

                                    intercepted_by = (enemy, e_slot, e_s_idx)
                                    break
                        if intercepted_by: break

                # Если найден РЕАЛЬНЫЙ перехватчик (я бил другого, а он меня поймал)
                if intercepted_by:
                    enemy, e_slot, e_s_idx = intercepted_by
                    my_slot['ui_status'] = {
                        "text": f"CLASH vs {enemy.name} [S{e_s_idx + 1}] | Перехвачен ({my_slot['speed']} < {e_slot['speed']})",
                        "icon": "⚠️",
                        "color": "orange"
                    }
                    continue

                # --- ДАЛЕЕ СТАНДАРТНАЯ ЛОГИКА ---
                if t_u_idx == -1 or t_u_idx >= len(target_team_list):
                    my_slot['ui_status'] = {"text": "НЕТ ЦЕЛИ", "icon": "⛔", "color": "gray"}
                    continue

                target_unit = target_team_list[t_u_idx]
                if target_unit.is_dead():
                    my_slot['ui_status'] = {"text": "ЦЕЛЬ МЕРТВА", "icon": "💀", "color": "gray"}
                    continue

                my_spd = my_slot['speed']
                tgt_spd = "?"
                tgt_slot_label = "?"
                target_slot = None

                if t_s_idx != -1 and t_s_idx < len(target_unit.active_slots):
                    target_slot = target_unit.active_slots[t_s_idx]
                    tgt_spd = target_slot['speed']
                    tgt_slot_label = f"S{t_s_idx + 1}"

                if is_friendly:
                    my_slot['ui_status'] = {"text": f"BUFF -> {target_unit.name}", "icon": "✨", "color": "green"}
                    continue

                is_mutual = False
                if target_slot:
                    if target_slot.get('target_unit_idx') == my_idx and \
                            target_slot.get('target_slot_idx') == my_slot_idx:
                        is_mutual = True

                if my_slot.get('force_onesided'):
                    my_slot['ui_status'] = {
                        "text": f"ONE SIDED (Провал) -> {target_unit.name} | Слаб",
                        "icon": "🐌",
                        "color": "orange"
                    }

                elif my_slot.get('force_clash'):
                    if is_mutual:
                        reason = f"Взаимно ({my_spd} vs {tgt_spd})"
                        icon = "⚔️"
                    else:
                        reason = f"Перехват! ({my_spd} > {tgt_spd})"
                        icon = "⚡"

                    my_slot['ui_status'] = {
                        "text": f"CLASH vs {target_unit.name} [{tgt_slot_label}] | {reason}",
                        "icon": icon,
                        "color": "red"
                    }

                elif is_mutual:
                    # Сюда попадет тот, кто проиграл по скорости в взаимном клэше
                    # (потому что у него нет force_clash, но is_mutual=True)
                    my_slot['ui_status'] = {
                        "text": f"CLASH vs {target_unit.name} [{tgt_slot_label}] | Взаимно ({my_spd} vs {tgt_spd})",
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

def use_item_action(unit, card):
    """
    Мгновенно применяет эффект предмета.
    """
    # Логируем действие
    msg = f"💊 **{unit.name}** uses **{card.name}**!"

    # Запускаем скрипты карты (триггер "on_use")
    # Создаем список для логов конкретно этого действия
    item_logs = [msg]

    # Используем process_card_self_scripts, передавая item_logs как custom_log_list
    # target=None, так как предметы обычно на себя (self). Если нужен таргет, придется усложнять UI.
    # Пока считаем, что таблетки пьют сами.
    from logic.mechanics.scripts import process_card_self_scripts
    process_card_self_scripts("on_use", unit, None, logs=None, custom_log_list=item_logs, card_override=card)
    # Добавляем в общий лог боя
    st.session_state['battle_logs'].append({
        "round": "Item",
        "rolls": "Consumable",
        "details": item_logs
    })

def render_inventory(unit, unit_key):
    """
    Рендерит секцию инвентаря с предметами (CardType.ITEM).
    """
    # Фильтруем карты в колоде, оставляя только предметы
    inventory_cards = []
    if unit.deck:
        for cid in unit.deck:
            card = Library.get_card(cid)
            # Проверяем тип
            if card and str(card.card_type).lower() == "item":
                inventory_cards.append(card)

    if not inventory_cards:
        return

    with st.expander("🎒 Inventory (Consumables)", expanded=False):
        for card in inventory_cards:
            btn_key = f"use_item_{unit_key}_{card.id}"
            desc = card.description if card.description else "No description"

            # Кнопка использования
            if st.button(f"💊 {card.name}", key=btn_key, help=desc, use_container_width=True):
                from ui.simulator.simulator_logic import use_item_action
                use_item_action(unit, card)
                st.rerun()