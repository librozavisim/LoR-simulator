import copy
import streamlit as st
from ui.app_modules.state_controller import update_and_save_state

def render_team_builder_sidebar():
    """
    Отрисовывает инструменты добавления/удаления юнитов (только для Симулятора).
    """
    st.sidebar.divider()
    st.sidebar.subheader("⚔️ Team Builder")

    current_phase = st.session_state.get('phase', 'roll')
    is_team_locked = current_phase != 'roll'

    if is_team_locked:
        st.sidebar.info("🔒 Идет бой. Изменение команд заблокировано.")

    roster_keys = sorted(list(st.session_state['roster'].keys()))

    # Выбор юнита
    unit_to_add_name = st.sidebar.selectbox(
        "Выберите персонажа", roster_keys, key="sim_unit_add_sel", disabled=is_team_locked
    )

    as_template = st.sidebar.checkbox(
        "Добавить как копию (Шаблон)", value=False,
        help="Вкл: создает независимую копию. Выкл: добавляет ссылку на оригинал.",
        disabled=is_team_locked
    )

    def add_unit_to_team(target_list_key):
        if not unit_to_add_name: return
        base_unit = st.session_state['roster'][unit_to_add_name]
        unit_to_add = None

        if as_template:
            unit_to_add = copy.deepcopy(base_unit)
            existing_names = [u.name for u in st.session_state['team_left'] + st.session_state['team_right']]
            count = 0
            for name in existing_names:
                if name.startswith(base_unit.name): count += 1
            if count > 0:
                unit_to_add.name = f"{base_unit.name} {count + 1}"
        else:
            all_current_units = st.session_state['team_left'] + st.session_state['team_right']
            if any(u is base_unit for u in all_current_units):
                st.sidebar.error(f"❌ {base_unit.name} уже в команде!")
                return
            unit_to_add = base_unit

        # Init memory
        unit_to_add.memory['start_of_battle_stats'] = {
            'hp': unit_to_add.current_hp,
            'sp': unit_to_add.current_sp,
            'stagger': unit_to_add.current_stagger
        }

        st.session_state[target_list_key].append(unit_to_add)
        st.session_state['battle_logs'] = []
        update_and_save_state()

    c_add_l, c_add_r = st.sidebar.columns(2)
    if c_add_l.button("⬅️ Add Left", width='stretch', disabled=is_team_locked):
        add_unit_to_team('team_left')
        st.rerun()
    if c_add_r.button("Add Right ➡️", width='stretch', disabled=is_team_locked):
        add_unit_to_team('team_right')
        st.rerun()

    st.sidebar.markdown("---")

    def remove_unit(team_key, idx):
        st.session_state[team_key].pop(idx)
        update_and_save_state()
        st.rerun()

    # Списки команд в сайдбаре
    st.sidebar.markdown(f"**Left Team ({len(st.session_state['team_left'])})**")
    if st.session_state['team_left']:
        for i, u in enumerate(st.session_state['team_left']):
            c_name, c_del = st.sidebar.columns([4, 1])
            c_name.caption(f"{i + 1}. {u.name} (Lvl {u.level})")
            if c_del.button("❌", key=f"del_l_{i}", disabled=is_team_locked):
                remove_unit('team_left', i)
    else: st.sidebar.caption("Пусто")

    st.sidebar.markdown(f"**Right Team ({len(st.session_state['team_right'])})**")
    if st.session_state['team_right']:
        for i, u in enumerate(st.session_state['team_right']):
            c_name, c_del = st.sidebar.columns([4, 1])
            c_name.caption(f"{i + 1}. {u.name} (Lvl {u.level})")
            if c_del.button("❌", key=f"del_r_{i}", disabled=is_team_locked):
                remove_unit('team_right', i)
    else: st.sidebar.caption("Пусто")

    if st.sidebar.button("🗑️ Очистить все команды", width='stretch', disabled=is_team_locked):
        st.session_state['team_left'] = []
        st.session_state['team_right'] = []
        st.session_state['battle_logs'] = []
        update_and_save_state()
        st.rerun()