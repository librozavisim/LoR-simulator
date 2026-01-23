import streamlit as st

from ui.profile.stats.attributes import get_mod_value  # Reuse helper

SKILL_LABELS = {
    "strike_power": "Сила удара", "medicine": "Медицина", "willpower": "Сила воли",
    "acrobatics": "Акробатика", "shields": "Щиты",
    "tough_skin": "Крепкая кожа", "speed": "Скорость",
    "light_weapon": "Лёгкое оружие", "medium_weapon": "Среднее оружие",
    "heavy_weapon": "Тяжёлое оружие", "firearms": "Огнестрел",
    "eloquence": "Красноречие", "forging": "Ковка",
    "engineering": "Инженерия", "programming": "Программирование"
}

def render_luck(unit, u_key):
    st.divider()
    st.subheader("🍀 Удача")
    l_col1, l_col2, _ = st.columns([1, 1, 2])

    with l_col1:
        st.caption("Стат (Навык)")
        base_luck = unit.skills.get("luck", 0)
        total_luck = get_mod_value(unit, "luck", base_luck)

        lc_in, lc_val = st.columns([1.5, 1])
        with lc_in:
            new_luck_skill = st.number_input("Luck Skill", 0, 999, base_luck, label_visibility="collapsed", key=f"luck_sk_{u_key}")
            if new_luck_skill != base_luck:
                unit.skills["luck"] = new_luck_skill
                unit.recalculate_stats()
                st.rerun()

        with lc_val:
            st.write("")
            if total_luck > new_luck_skill:
                st.markdown(f":green[**{total_luck}**]")
            elif total_luck < new_luck_skill:
                st.markdown(f":red[**{total_luck}**]")
            else:
                st.markdown(f"**{total_luck}**")

    with l_col2:
        st.caption("Текущая (Points)")
        cur_luck = unit.resources.get("luck", 0)
        new_cur_luck = st.number_input("Current Luck", -999, 999, cur_luck, label_visibility="collapsed", key=f"luck_res_{u_key}")
        if new_cur_luck != cur_luck:
            unit.resources["luck"] = new_cur_luck
            st.rerun()

def render_skills(unit, u_key):
    st.markdown("")
    with st.expander("📚 Остальные навыки", expanded=True):
        scols = st.columns(3)
        skill_list = list(SKILL_LABELS.keys())

        for i, k in enumerate(skill_list):
            col_idx = i % 3
            with scols[col_idx]:
                base_val = unit.skills.get(k, 0)
                total_val = get_mod_value(unit, k, base_val)

                st.caption(SKILL_LABELS[k])
                c_in, c_val = st.columns([1.5, 1])
                with c_in:
                    new_base = st.number_input("S", 0, 999, base_val, key=f"sk_{k}_{u_key}", label_visibility="collapsed")
                    if new_base != base_val:
                        unit.skills[k] = new_base
                        unit.recalculate_stats()
                        st.rerun()

                with c_val:
                    st.write("")
                    if total_val > new_base:
                        st.markdown(f":green[**{total_val}**]")
                    elif total_val < new_base:
                        st.markdown(f":red[**{total_val}**]")
                    else:
                        st.markdown(f"**{total_val}**")