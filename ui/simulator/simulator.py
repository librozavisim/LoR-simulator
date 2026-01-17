import streamlit as st
from ui.components import render_unit_stats
# Импортируем обновленные функции логики
from ui.simulator.logic.simulator_logic import (
    roll_phase, execute_combat_auto, reset_game,
    sync_state_from_widgets, precalculate_interactions
)
from ui.simulator.components.simulator_components import render_slot_strip, render_active_abilities, render_inventory

# [NEW] Импорт логгера
from core.logging import logger


def render_simulator_page():
    # Инициализация фазы
    if 'phase' not in st.session_state: st.session_state['phase'] = 'roll'
    if 'round_number' not in st.session_state: st.session_state['round_number'] = 1

    # === ОБНОВЛЕННЫЕ СТИЛИ (CSS) ===
    st.markdown(f"""
        <style>
            /* Контейнер для счетчика */
            .turn-counter-static {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px auto; 
                padding: 10px 40px;
                width: fit-content;
                min-width: 150px;
                background: linear-gradient(135deg, rgba(35, 37, 46, 1) 0%, rgba(20, 20, 25, 1) 100%);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}

            .counter-label {{
                font-family: sans-serif; font-size: 11px; letter-spacing: 2px;
                text-transform: uppercase; color: #8d99ae; margin-bottom: 4px;
            }}

            .counter-value {{
                font-family: 'Courier New', monospace; font-size: 32px;
                font-weight: 700; color: #edf2f4; text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
                line-height: 1;
            }}

            /* [NEW] Стиль для системного лога */
            .log-entry {{
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 4px 8px;
                border-bottom: 1px solid #333;
                display: flex;
            }}
            .log-time {{ color: #6c757d; margin-right: 10px; min-width: 80px; }}
            .log-cat {{ color: #ffd166; margin-right: 10px; font-weight: bold; min-width: 80px; }}
            .log-msg {{ color: #e9ecef; word-break: break-word; }}
            .log-verbose {{ color: #adb5bd; }}
        </style>

        <div class="turn-counter-static">
            <div class="counter-label">SCENE</div>
            <div class="counter-value">{st.session_state['round_number']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Сайдбар с кнопкой сброса
    with st.sidebar:
        st.divider()
        # [UPD] Добавляем очистку логгера при сбросе
        if st.button("🔄 Reset Battle", type="secondary", use_container_width=True):
            reset_game()
            logger.clear()  # Очищаем системный лог
            st.rerun()

    # Получаем команды
    team_left = st.session_state.get('team_left', [])
    team_right = st.session_state.get('team_right', [])

    if not team_left or not team_right:
        st.warning("Teams are empty. Please configure teams in the sidebar.")
        return

    # 1. Пересчет статов
    for u in team_left + team_right:
        u.recalculate_stats()

    # 2. Синхронизация и прекалькуляция (только в фазе планирования)
    if st.session_state['phase'] == 'planning':
        sync_state_from_widgets(team_left, team_right)
        precalculate_interactions(team_left, team_right)

    # === ОСНОВНАЯ РАЗМЕТКА ===
    col_left_main, col_right_main = st.columns(2, gap="large")

    # --- LEFT TEAM ---
    with col_left_main:
        st.subheader(f"Left Team ({len(team_left)})")
        for i, unit in enumerate(team_left):
            with st.container(border=True):
                c_stats, c_img = st.columns([2, 1.2])
                with c_stats:
                    render_unit_stats(unit)
                with c_img:
                    img = unit.avatar if unit.avatar else "https://placehold.co/150?text=U"
                    st.image(img, use_column_width=True)

                render_active_abilities(unit, f"l_abil_{i}")
                render_inventory(unit, f"l_inv_{i}")

                if st.session_state['phase'] == 'planning':
                    st.divider()
                    if unit.active_slots:
                        for s_i in range(len(unit.active_slots)):
                            render_slot_strip(unit, team_right, team_left, s_i, f"l_{i}")
                    else:
                        st.caption("No active slots")

    # --- RIGHT TEAM ---
    with col_right_main:
        st.subheader(f"Right Team ({len(team_right)})")
        for i, unit in enumerate(team_right):
            with st.container(border=True):
                c_stats, c_img = st.columns([2, 1.2])
                with c_stats:
                    render_unit_stats(unit)
                with c_img:
                    img = unit.avatar if unit.avatar else "https://placehold.co/150?text=E"
                    st.image(img, use_column_width=True)

                render_active_abilities(unit, f"r_abil_{i}")
                render_inventory(unit, f"r_inv_{i}")

                if st.session_state['phase'] == 'planning':
                    st.divider()
                    if unit.active_slots:
                        for s_i in range(len(unit.active_slots)):
                            render_slot_strip(unit, team_left, team_right, s_i, f"r_{i}")
                    else:
                        st.caption("No active slots")

    st.divider()

    # === ЦЕНТРАЛЬНЫЕ КНОПКИ УПРАВЛЕНИЯ ===
    _, c_center, _ = st.columns([1, 2, 1])
    with c_center:
        if st.session_state['phase'] == 'roll':
            st.button("🎲 ROLL INITIATIVE (ALL)", type="primary", on_click=roll_phase, use_container_width=True)
        else:
            st.button("⚔️ FIGHT! (Execute Turn)", type="primary", on_click=execute_combat_auto,
                      use_container_width=True)

    # === ВИЗУАЛЬНЫЙ ОТЧЕТ (Карточки) ===
    st.subheader("📜 Battle Report")

    if st.session_state.get('turn_message'):
        st.info(st.session_state['turn_message'])

    visual_logs = st.session_state.get('battle_logs', [])

    if visual_logs:
        # Прячем визуальные логи в экспандер, чтобы не занимать место, если нужен дебаг
        with st.expander("Show Visual Clash Report", expanded=True):
            for log in visual_logs:
                if "left" in log and "right" in log:
                    with st.container(border=True):
                        l = log['left']
                        r = log['right']
                        c_vis_l, c_vis_c, c_vis_r = st.columns([5, 1, 5])

                        with c_vis_l:
                            st.markdown(
                                f"<div style='text-align:right'><b>{l['unit']}</b> <span style='color:gray'>({l['card']})</span><br>{l['dice']} <span style='font-size:1.2em; font-weight:bold'>{l['val']}</span> <span style='font-size:0.8em'>[{l['range']}]</span></div>",
                                unsafe_allow_html=True)
                        with c_vis_c:
                            st.markdown("<div style='text-align:center; padding-top:10px; color:gray'>VS</div>",
                                        unsafe_allow_html=True)
                        with c_vis_r:
                            st.markdown(
                                f"<b>{r['unit']}</b> <span style='color:gray'>({r['card']})</span><br><span style='font-size:0.8em'>[{r['range']}]</span> <span style='font-size:1.2em; font-weight:bold'>{r['val']}</span> {r['dice']}",
                                unsafe_allow_html=True)

                        st.divider()
                        st.caption(f"Result: {log.get('outcome', '-')}")
                        if 'details' in log:
                            for d in log['details']:
                                st.markdown(f"• {d}")

                else:
                    st.caption(f"ℹ️ {log.get('round', '')}: {log.get('details', '')}")

    # === [NEW] СИСТЕМНЫЙ ЛОГ (ТЕКСТОВЫЙ) ===
    st.divider()
    with st.expander("🛠️ System Logs (Debug Console)", expanded=False):
        c_filter_lvl, c_filter_cat = st.columns(2)

        # 1. Фильтр уровня
        # Маппинг UI имен на значения Enum
        lvl_map = {"Minimal": 1, "Normal": 2, "Verbose": 3}
        selected_lvl_name = c_filter_lvl.selectbox("Log Level", ["Normal", "Verbose", "Minimal"], index=0)
        selected_lvl_val = lvl_map[selected_lvl_name]

        # 2. Получаем отфильтрованные по уровню логи
        # (logger импортирован из core.logging)
        system_logs = logger.get_logs_for_ui(selected_lvl_val)

        # 3. Фильтр категорий
        if system_logs:
            all_cats = sorted(list(set(l['category'] for l in system_logs)))
            selected_cats = c_filter_cat.multiselect("Category", all_cats, default=all_cats)
        else:
            selected_cats = []

        # 4. Рендер логов
        log_html = ""
        for entry in system_logs:
            if entry['category'] in selected_cats:
                # Серый цвет для Verbose, белый для остальных
                css_class = "log-verbose" if entry['level'] == 3 else "log-msg"

                log_html += f"""
                <div class="log-entry">
                    <span class="log-time">[{entry['time']}]</span>
                    <span class="log-cat">{entry['category']}</span>
                    <span class="{css_class}">{entry['message']}</span>
                </div>
                """

        if log_html:
            st.markdown(log_html, unsafe_allow_html=True)
        else:
            st.caption("No logs found. Try changing filters or running a battle.")