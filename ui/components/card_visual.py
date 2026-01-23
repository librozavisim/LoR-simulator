import streamlit as st
from core.card import Card
from ui.icons import get_icon_html
from ui.styles import TYPE_COLORS
from ui.components.script_formatter import _format_script_text

def render_card_visual(card: Card, is_staggered: bool = False):
    """Визуальное представление карты с кубиками."""
    with st.container(border=True):
        if is_staggered:
            st.error("😵 STAGGERED")
            return
        if not card:
            st.warning("No card selected")
            return

        type_icon = "🏹" if card.card_type == "ranged" else "⚔️"
        st.markdown(f"**{card.name}** {type_icon}")

        if card.scripts:
            for trig, scripts in card.scripts.items():
                trigger_name = trig.replace("_", " ").title()
                st.markdown(f"**{trigger_name}:**")
                for s in scripts:
                    friendly_text = _format_script_text(s['script_id'], s.get('params', {}))
                    st.caption(f"- {friendly_text}", unsafe_allow_html=True)

        st.divider()

        cols = st.columns(len(card.dice_list)) if card.dice_list else [st]
        for i, dice in enumerate(card.dice_list):
            with cols[i]:
                color = TYPE_COLORS.get(dice.dtype, "black")
                dtype_key = dice.dtype.name.lower()
                icon_html = get_icon_html(dtype_key, width=24)

                st.markdown(f"{icon_html} : {color}[**{dice.min_val}-{dice.max_val}**]", unsafe_allow_html=True)

                if dice.scripts:
                    for trig, effs in dice.scripts.items():
                        for e in effs:
                            friendly_text = _format_script_text(e['script_id'], e.get('params', {}))
                            st.caption(f"*{friendly_text}*", unsafe_allow_html=True)