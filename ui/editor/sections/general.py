import streamlit as st


def render_general_info():
    """
    Отрисовывает основные поля: Имя, Тип, Флаги, Описание.
    """
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        name = c1.text_input("Название карты", key="ed_name")
        tier = c2.selectbox("Tier (Ранг)", [1, 2, 3, 4, 5], key="ed_tier")
        ctype = c3.selectbox("Тип",
                             ["Melee", "Offensive", "Ranged", "Mass Summation", "Mass Individual", "On Play", "Item"],
                             key="ed_type")

        # === ФЛАГИ С ПРЕДПРОСМОТРОМ ===
        c_flags, c_preview = st.columns([3, 2])

        with c_flags:
            flags = st.multiselect("Флаги", ["friendly", "offensive", "unchangeable", "exhaust"], key="ed_flags")

        with c_preview:
            has_friendly = "friendly" in flags
            has_offensive = "offensive" in flags

            tgt_icon = "⚔️"
            tgt_text = "Враги (Default)"
            tgt_color = "red"

            if has_friendly and has_offensive:
                tgt_icon = "⚔️+🛡️"
                tgt_text = "Гибрид"
                tgt_color = "orange"
            elif has_friendly:
                tgt_icon = "🛡️"
                tgt_text = "Союзники (Buff)"
                tgt_color = "green"
            elif has_offensive:
                tgt_icon = "⚔️"
                tgt_text = "Враги"
                tgt_color = "red"

            st.markdown("**Режим:**")
            st.markdown(f":{tgt_color}[## {tgt_icon} {tgt_text}]")

        desc = st.text_area("Описание", key="ed_desc", height=68)
        save_file = st.session_state.get("ed_source_file", "custom_cards.json")
        st.caption(f"📂 Файл сохранения: `{save_file}`")

    return name, tier, ctype, desc