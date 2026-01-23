import streamlit as st
from core.library import Library
from logic.state.state_manager import StateManager

def save_cb():
    StateManager.save_state(st.session_state)

def resolve_slot_card(slot):
    """
    Убеждается, что в слоте лежит объект Card, а не строка ID.
    """
    selected_card = slot.get('card')
    if selected_card and not hasattr(selected_card, 'dice_list'):
        try:
            resolved = Library.get_card(selected_card)
            if hasattr(resolved, 'dice_list'):
                slot['card'] = resolved
                return resolved
            else:
                slot['card'] = None
                return None
        except Exception:
            slot['card'] = None
            return None
    return selected_card