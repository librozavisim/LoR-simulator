import streamlit as st

from core.logging import logger, LogLevel
from logic.state.state_manager import StateManager
from ui.simulator.logic.step_func import reset_game


def render_sidebar():
    with st.sidebar:
        st.divider()
        st.subheader("⚙️ Управление боем")

        # 1. СБРОС
        if st.button("🔄 Сброс боя (Reset)", type="secondary", width='stretch', help="Полный сброс к началу"):
            reset_game()
            logger.clear()
            st.rerun()

        # 2. МАШИНА ВРЕМЕНИ
        undo_stack = st.session_state.get('undo_stack', [])
        if undo_stack:
            with st.expander("🕰️ История ходов", expanded=True):
                available_rounds = list(range(1, len(undo_stack) + 1))
                target_round = st.selectbox(
                    "Вернуться к началу раунда:",
                    options=available_rounds,
                    index=len(available_rounds) - 1,
                    format_func=lambda x: f"Раунд {x}",
                    key="timeline_selector"
                )

                if st.button("⏪ Загрузить состояние", type="primary", width='stretch'):
                    stack_index = target_round - 1
                    if 0 <= stack_index < len(undo_stack):
                        snapshot = undo_stack[stack_index]
                        if snapshot.get("type") == "dynamic":
                            base_snapshot = undo_stack[0]
                            if base_snapshot.get("type") != "full":
                                st.error("❌ Ошибка истории: Базовый снимок поврежден!")
                            else:
                                StateManager.restore_from_dynamic_snapshot(st.session_state, snapshot, base_snapshot)
                                st.toast(f"Раунд {target_round} восстановлен (Delta)! 🕰️")
                        else:
                            StateManager.restore_state_from_snapshot(st.session_state, snapshot)
                            st.toast(f"Раунд {target_round} восстановлен (Full)! 🕰️")

                        st.session_state['undo_stack'] = undo_stack[:stack_index + 1]
                        st.rerun()
        else:
            st.caption("История ходов пуста (Раунд 1)")

        st.divider()

        # 3. ЛОГИРОВАНИЕ
        st.markdown("**📜 Уровень Логирования**")
        log_mode = st.radio(
            "Детализация:", ["Минимальный", "Обычный", "Подробный"], index=1, key="sim_log_mode"
        )

        log_level_map = {
            "Минимальный": LogLevel.MINIMAL,
            "Обычный": LogLevel.NORMAL,
            "Подробный": LogLevel.VERBOSE
        }
        return log_level_map[log_mode], log_mode