import streamlit as st

from core.unit.unit import Unit


def render_combat_info(unit: Unit):
    """Отображает сопротивления и боевые бонусы."""
    with st.expander("🛡️ Resists & Bonuses", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Slash", f"x{unit.hp_resists.slash}")
        c2.metric("Pierce", f"x{unit.hp_resists.pierce}")
        c3.metric("Blunt", f"x{unit.hp_resists.blunt}")

        st.divider()

        mods = unit.modifiers
        atk_power = mods.get("power_attack", 0) + mods.get("power_medium", 0)
        def_block = mods.get("power_block", 0)
        def_evade = mods.get("power_evade", 0)
        init_bonus = mods.get("initiative", 0)

        b1, b2, b3 = st.columns(3)
        b1.metric("⚔️ Atk Power", f"+{atk_power}")
        b2.metric("🛡️ Block", f"+{def_block}")
        b3.metric("💨 Evade", f"+{def_evade}")

        st.caption(f"Init Bonus: +{init_bonus}")