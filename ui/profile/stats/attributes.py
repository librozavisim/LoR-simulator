import streamlit as st

ATTR_LABELS = {
    "strength": "Сила", "endurance": "Стойкость", "agility": "Ловкость",
    "wisdom": "Мудрость", "psych": "Психика"
}


def get_mod_value(unit, key, default=0):
    val = unit.modifiers.get(key, default)
    if isinstance(val, dict):
        return val.get("flat", default)
    return val


def render_attributes(unit, u_key):
    """Отрисовка характеристик (Сила, Ловкость...)."""
    st.subheader("Характеристики")
    acols = st.columns(5)

    for i, k in enumerate(ATTR_LABELS.keys()):
        base_val = unit.attributes.get(k, 0)
        total_val = get_mod_value(unit, k, base_val)

        with acols[i]:
            st.caption(ATTR_LABELS[k])
            c_in, c_val = st.columns([1.5, 1])
            with c_in:
                new_base = st.number_input("Base", 0, 999, base_val, key=f"attr_{k}_{u_key}",
                                           label_visibility="collapsed")
                if new_base != base_val:
                    unit.attributes[k] = new_base
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