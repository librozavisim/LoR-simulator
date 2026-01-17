import streamlit as st
from core.unit.unit import Unit
from core.unit.unit_library import UnitLibrary
from core.logging import logger, LogLevel  # [ВАЖНО] Импорт логгера

# Import our new components
from ui.profile.header import render_header, render_basic_info
from ui.profile.stats import render_stats
from ui.profile.equipment import render_equipment
from ui.profile.abilities import render_abilities


def render_profile_page():
    if 'roster' not in st.session_state or not st.session_state['roster']:
        st.session_state['roster'] = UnitLibrary.load_all() or {"New Unit": Unit("New Unit")}

    roster = st.session_state['roster']

    # 1. Header & Selection
    unit, u_key = render_header(roster)

    # === ПЕРЕСЧЕТ ХАРАКТЕРИСТИК (В НАЧАЛЕ) ===
    # Мы делаем это ДО отрисовки компонентов, чтобы:
    # 1. Получить чистый лог расчетов (очистив старый мусор).
    # 2. Обновить значения unit (HP, SP и т.д.), чтобы render_stats показал актуальные цифры.

    logger.clear()  # Очищаем логгер перед расчетом
    unit.recalculate_stats()  # Запускаем расчет (он пишет в logger)
    calculation_logs = logger.get_logs()  # Забираем то, что насчитали

    # === ОТРИСОВКА ИНТЕРФЕЙСА ===
    col_l, col_r = st.columns([1, 2.5], gap="medium")

    # 2. Left Column: Basic Info
    with col_l:
        render_basic_info(unit, u_key)

    # 3. Right Column: Everything else
    with col_r:
        render_equipment(unit, u_key)
        render_stats(unit, u_key)

    st.markdown("---")

    # 4. Abilities & Deck
    render_abilities(unit, u_key)

    # 5. Calculation Log (Показываем собранные логи)
    with st.expander("📜 Лог расчета характеристик", expanded=False):
        if calculation_logs:
            for l in calculation_logs:
                # Цветовое выделение для читаемости
                if "Stats" in str(l) or "Talent" in str(l):
                    st.caption(f"• {l}")
                elif "ERROR" in str(l):
                    st.error(f"• {l}")
                else:
                    st.text(f"• {l}")
        else:
            st.info("Нет записей. Проверьте уровень логирования или наличие пассивок.")