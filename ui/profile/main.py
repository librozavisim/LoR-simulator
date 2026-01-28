import streamlit as st
import io
from fpdf import FPDF

from core.logging import logger  # [ВАЖНО] Импорт логгера
from core.unit.unit import Unit
from core.unit.unit_library import UnitLibrary
from ui.profile.abilities import render_abilities
from ui.profile.equipment import render_equipment
from ui.profile.header import render_header, render_basic_info
from ui.profile.stats import render_stats


def render_profile_page():
    if 'roster' not in st.session_state or not st.session_state['roster']:
        st.session_state['roster'] = UnitLibrary.load_all() or {"New Unit": Unit("New Unit")}

    roster = st.session_state['roster']

    # 1. Header & Selection
    unit, u_key = render_header(roster)
    if unit is None:
        return  # ничего не показываем, если персонажа нет

    # === ПЕРЕСЧЕТ ХАРАКТЕРИСТИК (В НАЧАЛЕ) ===
    logger.clear()  # Очищаем логгер перед расчетом
    unit.recalculate_stats()  # Обновляем HP, SP, навыки и т.д.
    calculation_logs = logger.get_logs()  # Логи пересчета

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

    # 5. Calculation Log
    with st.expander("📜 Лог расчета характеристик", expanded=False):
        if calculation_logs:
            for l in calculation_logs:
                if "Stats" in str(l) or "Talent" in str(l):
                    st.caption(f"• {l}")
                elif "ERROR" in str(l):
                    st.error(f"• {l}")
                else:
                    st.text(f"• {l}")
        else:
            st.info("Нет записей. Проверьте уровень логирования или наличие пассивок.")

    st.divider()

    # pdf generation
    st.markdown("## Get charshit in PDF")

    def create_character_pdf(unit):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        lines = []

        lines.append(unit.name)
        lines.append(f"Уровень: {unit.level}")
        lines.append(f"Ранг: {unit.rank}")
        lines.append(f"Базовый интеллект: {unit.base_intellect}")
        lines.append(f"Накопленный опыт: {unit.total_xp}")
        lines.append("")

        lines.append("Текущее состояние")
        lines.append(f"HP: {unit.current_hp}")
        lines.append(f"SP: {unit.current_sp}")
        lines.append(f"Stagger: {unit.current_stagger}")
        luck = unit.resources.get("luck", 0)
        lines.append(f"Удача: {luck}")
        lines.append("")

        lines.append("Атрибуты")
        for attr, val in unit.attributes.items():
            lines.append(f"{attr.capitalize()}: {val}")
        lines.append("")

        lines.append("Навыки")
        for skill, val in unit.skills.items():
            lines.append(f"{skill.replace('_',' ').capitalize()}: {val}")
        lines.append("")

        lines.append("Пассивные способности")
        for passive_obj in getattr(unit, "passives", []):
            lines.append(f"— {passive_obj.name}: {passive_obj.description}")
        lines.append("")

        lines.append("Таланты")
        for idx, talent_obj in enumerate(getattr(unit, "talents", []), 1):
            lines.append(f"{idx}. {talent_obj.name}: {talent_obj.description}")
        lines.append("")

        lines.append("Биография")
        lines.extend(unit.biography.split("\n"))

        for line in lines:
            pdf.multi_cell(0, 6, txt=line)

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    if st.button("Download PDF"):
        pdf_buffer = create_character_pdf(unit)
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name=f"{unit.name}_report.pdf",
            mime="application/pdf"
        )
