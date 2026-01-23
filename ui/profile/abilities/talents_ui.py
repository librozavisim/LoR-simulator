import streamlit as st
from logic.character_changing.passives import PASSIVE_REGISTRY
from logic.character_changing.talents import TALENT_REGISTRY


def fmt_name(aid):
    if aid in TALENT_REGISTRY: return f"★ {TALENT_REGISTRY[aid].name}"
    if aid in PASSIVE_REGISTRY: return f"🛡️ {PASSIVE_REGISTRY[aid].name}"
    return aid


def render_talents_ui(unit, u_key):
    st.subheader("🧬 Таланты и Пассивки")
    c_tal, c_desc = st.columns([2, 1])

    with c_tal:
        # --- TALENTS ---
        bonus_slots = int(unit.modifiers["talent_slots"]["flat"])
        max_talents = (unit.level // 3) + bonus_slots
        if max_talents < 0: max_talents = 0

        current_talents = [t for t in unit.talents if t in TALENT_REGISTRY]
        talents_key = f"mt_{u_key}"
        session_selection = st.session_state.get(talents_key, [])

        # Защита от краша при уменьшении лимита
        safe_limit = max(max_talents, len(current_talents), len(session_selection))

        st.markdown(f"**Таланты ({len(current_talents)} / {max_talents})**")

        if len(current_talents) > max_talents:
            st.warning(f"⚠️ Лимит превышен! Доступно: {max_talents}")

        new_talents = st.multiselect(
            "Список талантов",
            options=sorted(list(TALENT_REGISTRY.keys())),
            default=current_talents,
            format_func=fmt_name,
            max_selections=safe_limit,
            label_visibility="collapsed",
            key=talents_key
        )

        if new_talents != current_talents:
            old_unknowns = [t for t in unit.talents if t not in TALENT_REGISTRY]
            unit.talents = new_talents + old_unknowns
            unit.recalculate_stats()
            st.rerun()

        # --- PASSIVES ---
        st.markdown("**Пассивки**")
        current_passives = [p for p in unit.passives if p in PASSIVE_REGISTRY]

        new_passives = st.multiselect(
            "Список пассивок",
            options=sorted(list(PASSIVE_REGISTRY.keys())),
            default=current_passives,
            format_func=fmt_name,
            label_visibility="collapsed",
            key=f"mp_{u_key}"
        )
        if new_passives != current_passives:
            old_unknowns = [p for p in unit.passives if p not in PASSIVE_REGISTRY]
            unit.passives = new_passives + old_unknowns
            unit.recalculate_stats()
            st.rerun()

    with c_desc:
        st.info("ℹ️ **Эффекты:**")
        all_ids = unit.talents + unit.passives
        if not all_ids:
            st.caption("Пусто")
        for aid in all_ids:
            obj = TALENT_REGISTRY.get(aid) or PASSIVE_REGISTRY.get(aid)
            if obj:
                with st.expander(obj.name):
                    st.write(obj.description)