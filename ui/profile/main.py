import streamlit as st
import io
import os
from fpdf import FPDF

from core.logging import logger
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

    unit, u_key = render_header(roster)
    if unit is None:
        return

    logger.clear()
    unit.recalculate_stats()
    calculation_logs = logger.get_logs()

    col_l, col_r = st.columns([1, 2.5], gap="medium")

    with col_l:
        render_basic_info(unit, u_key)

    with col_r:
        render_equipment(unit, u_key)
        render_stats(unit, u_key)

    st.markdown("---")
    render_abilities(unit, u_key)

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
    st.markdown("## Скачать профиль в PDF")

    def create_character_pdf(unit: Unit) -> io.BytesIO:
        pdf = FPDF()
        pdf.add_page()

        font_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans", "DejaVuSans.ttf")
        )
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)

        page_width = pdf.w - 2 * pdf.l_margin
        line_height = 6

        lines = [
            unit.name,
            f"Уровень: {unit.level}",
            f"Ранг: {unit.rank}",
            f"Базовый интеллект: {unit.base_intellect}",
            f"Накопленный опыт: {unit.total_xp}",
            "",
            "Текущее состояние",
            f"HP: {unit.current_hp}",
            f"SP: {unit.current_sp}",
            f"Stagger: {unit.current_stagger}",
            f"Удача: {unit.resources.get('luck', 0)}",
            "",
            "Атрибуты",
        ]

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
            words = line.split(" ")
            current_line = ""
            for word in words:
                if pdf.get_string_width(current_line + " " + word) > page_width:
                    pdf.multi_cell(page_width, line_height, current_line, align="L")
                    current_line = word
                else:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
            if current_line:
                pdf.multi_cell(page_width, line_height, current_line, align="L")

        pdf_bytes = pdf.output(dest="S")
        return io.BytesIO(pdf_bytes)

    if st.button("Download"):
        pdf_buffer = create_character_pdf(unit)
        st.download_button(
            label="Download",
            data=pdf_buffer,
            file_name=f"{unit.name}_report.pdf",
            mime="application/pdf"
        )
