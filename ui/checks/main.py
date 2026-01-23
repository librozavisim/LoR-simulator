import streamlit as st
from ui.checks.constants import TYPE_10_ATTRS, TYPE_15_SKILLS
from ui.checks.components import draw_roll_interface, draw_luck_interface

def render_checks_page():
    st.title("🎲 Проверки (Skill Checks)")

    if 'roster' not in st.session_state or not st.session_state['roster']:
        st.warning("Ростер пуст.")
        return

    roster_names = sorted(list(st.session_state['roster'].keys()))
    current_key = st.session_state.get("checks_selected_unit")
    default_index = 0

    if current_key in roster_names:
        default_index = roster_names.index(current_key)

    c_sel, _ = st.columns([1, 1])
    selected_name = c_sel.selectbox(
        "Персонаж",
        roster_names,
        index=default_index,
        key="checks_selected_unit",
        on_change=st.session_state.get('save_callback')
    )

    unit = st.session_state['roster'][selected_name]
    unit.recalculate_stats()

    tabs = st.tabs(["💪 Характеристики", "🛠️ Навыки", "🧠 Мудрость", "🍀 Удача", "💡 Интеллект"])

    # 1. Характеристики
    with tabs[0]:
        l_dict = {v: k for k, v in TYPE_10_ATTRS.items()}
        chosen = st.selectbox("Параметр", list(TYPE_10_ATTRS.values()), key="sel_attr")
        st.caption("🎲 **1d6 + (Значение / 3)**. Макс стат: 30.")
        draw_roll_interface(unit, l_dict[chosen], chosen)
        with st.expander("ℹ️ Таблица Сложности (Характеристики)", expanded=True):
            st.markdown("""
                * **1~4** — дела, что может сделать любой...
                * **5~8** — небольшая подготовка...
                * **9~12** — обученные специалисты...
                * **13~16** — профессионалы...
                * **17~20** — нечеловеческий уровень...
                * **21+** — за гранью человеческого...
                """)

    # 2. Навыки
    with tabs[1]:
        l_dict = {v: k for k, v in TYPE_15_SKILLS.items()}
        items = sorted(list(TYPE_15_SKILLS.values()))
        chosen = st.selectbox("Выберите навык", items, key="sel_skill")
        key = l_dict[chosen]

        info_text = "🎲 **1d6 + Значение**."
        if key in ["speed", "medicine"]:
            info_text = "🎲 **1d6 + (Значение / 3)** (Атрибутивный расчет)"
        if key == "engineering": info_text += " ⚠️ Сложность x1.3"

        st.caption(info_text)
        draw_roll_interface(unit, key, chosen)
        with st.expander("ℹ️ Таблица Сложности (Навыки)", expanded=True):
            st.markdown("""
            * **1~7** — легко...
            * **8~14** — средняя сложность...
            * **15~21** — специалисты...
            * **22~29** — аугментации...
            * **30+** — за гранью...
            """)

    # 3. Мудрость
    with tabs[2]:
        st.caption("🎲 **1d20 + Значение**. Для ролевых ситуаций.")
        draw_roll_interface(unit, "wisdom", "Мудрость")
        with st.expander("ℹ️ Таблица Сложности (Мудрость)", expanded=True):
            st.markdown("""
            * **1~6** — легко...
            * **7~12** — норма...
            * **13~19** — сложно...
            * **20~27** — очень сложно...
            * **28~35** — эксперт...
            * **36~44** — сверхчеловек...
            * **45+** — божественно...
            """)

    # 4. Удача
    with tabs[3]:
        st.caption("🎲 **1d12 + Текущая Удача**. Трата удачи приводит к штрафам.")
        draw_luck_interface(unit)
        with st.expander("ℹ️ Уровни Удачи (ПОЛНОЕ ОПИСАНИЕ)", expanded=True):
            st.markdown("""
            * **1** — Неудачник (Свиппер)
            * **6** — Обычная удача
            * **12** — Везение (Монетка)
            * **20** — Куш в казино
            * **30** — Нереальное везение
            * **45** — Корни странностей
            * **60** — Потустороннее вмешательство
            * **80** — Влияние на историю
            * **100+** — Звезда Города
            """)

    # 5. Интеллект
    with tabs[4]:
        st.caption("🎲 **1d6 + 4 + Интеллект**.")
        draw_roll_interface(unit, "intellect", "Интеллект")
        with st.expander("ℹ️ Таблица Сложности (Интеллект)", expanded=True):
            st.markdown("""
            * **1~7** — Легко
            * **8~14** — Средне
            * **15~21** — Сложно
            * **22~29** — Сверхчеловечески
            * **30+** — Невозможно
            """)