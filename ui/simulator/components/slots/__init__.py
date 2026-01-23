import streamlit as st

from ui.simulator.components.slots.header import render_slot_header
from ui.simulator.components.slots.info import render_card_info
from ui.simulator.components.slots.selector import render_card_selector
from ui.simulator.components.slots.targeting import render_target_selector
from ui.simulator.components.slots.utils import resolve_slot_card


def render_slot_strip(unit, opposing_team, my_team, slot_idx, key_prefix):
    """
    Главная функция рендеринга слота. Собирает компоненты воедино.
    """
    slot = unit.active_slots[slot_idx]

    # 1. Проверка Stagger
    if slot.get('stunned'):
        st.error(f"😵 **STAGGERED** (Speed 0)")
        return

    # 2. Валидация карты (String ID -> Object)
    resolve_slot_card(slot)

    # 3. Заголовок
    label = render_slot_header(slot, slot_idx)

    # 4. Основной контейнер
    with st.expander(label, expanded=False):
        # Определение типа атаки происходит внутри targeting, но нам нужно знать лэйаут
        is_mass = False
        selected_card = slot.get('card')
        if selected_card:
            ctype = str(selected_card.card_type).lower()
            if "mass" in ctype: is_mass = True

        # Layout columns
        if is_mass:
            c_sel, c_mass = st.columns([1, 2])
            target_container = c_mass
        else:
            c_tgt, c_sel = st.columns([1, 1])
            target_container = c_tgt

        # Отрисовка селектора карты
        render_card_selector(c_sel, unit, slot, slot_idx, key_prefix)

        # Отрисовка выбора цели (использует нужный контейнер)
        render_target_selector(target_container, None if not is_mass else c_mass,
                               unit, slot, slot_idx, opposing_team, my_team, key_prefix)

        # Инфо о карте (кубики, эффекты)
        render_card_info(unit, slot)