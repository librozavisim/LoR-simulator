import streamlit as st

from ui.cheat_sheet.calculator import render_calculator_tab
from ui.cheat_sheet.static_tabs import (
    render_speed_tab, render_hp_tab, render_power_tab,
    render_eco_tab, render_mech_tab
)


def render_cheat_sheet_page():
    st.title("📚 Справочник характеристик")
    st.caption("Референсные значения и экономика Города.")

    tab_speed, tab_hp, tab_power, tab_eco, tab_mech, tab_balance = st.tabs([
        "💨 Скорость", "❤️ Здоровье", "⚔️ Сила", "💰 Экономика", "💀 Механики", "⚖️ Конструктор"
    ])

    with tab_speed: render_speed_tab()
    with tab_hp: render_hp_tab()
    with tab_power: render_power_tab()
    with tab_eco: render_eco_tab()
    with tab_mech: render_mech_tab()
    with tab_balance: render_calculator_tab()