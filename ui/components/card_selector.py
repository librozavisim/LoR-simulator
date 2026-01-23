import streamlit as st
from core.card import Card
from core.dice import Dice
from core.enums import DiceType
from core.library import Library
from core.unit.unit import Unit

def card_selector_ui(unit: Unit, key_prefix: str):
    """Выбор карты из библиотеки или создание кастомной."""
    mode = st.radio("Src", ["📚 Library", "🛠️ Custom"], key=f"{key_prefix}_mode", horizontal=True, label_visibility="collapsed")

    if mode == "📚 Library":
        all_cards_objs = Library.get_all_cards()
        if not all_cards_objs:
            st.error("Library empty!")
            return None

        selected_card = st.selectbox("Preset", all_cards_objs, format_func=lambda x: x.name, key=f"{key_prefix}_lib")
        if selected_card and selected_card.description:
            st.caption(f"📝 {selected_card.description}")

    else:
        with st.container(border=True):
            c_name = st.text_input("Name", "My Card", key=f"{key_prefix}_custom_name")
            num_dice = st.slider("Dice", 1, 4, 2, key=f"{key_prefix}_cnt")
            custom_dice = []
            for i in range(num_dice):
                c1, c2, c3 = st.columns([1.5, 1, 1])
                dtype_str = c1.selectbox("T", [t.name for t in DiceType], key=f"{key_prefix}_d_{i}_t", label_visibility="collapsed")
                dmin = c2.number_input("Min", 1, 50, 4, key=f"{key_prefix}_d_{i}_min", label_visibility="collapsed")
                dmax = c3.number_input("Max", 1, 50, 8, key=f"{key_prefix}_d_{i}_max", label_visibility="collapsed")
                custom_dice.append(Dice(dmin, dmax, DiceType[dtype_str]))

            selected_card = Card(name=c_name, dice_list=custom_dice, description="Custom Card")

    if not unit.is_staggered():
        unit.current_card = selected_card
    return unit.current_card