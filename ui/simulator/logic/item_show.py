import streamlit as st

from core.library import Library
# Импортируем скрипты механик
from logic.mechanics.scripts import process_card_self_scripts


def use_item_action(unit, card):
    # Проверка наличия доступных копий
    cds = unit.card_cooldowns.get(card.id, [])
    if isinstance(cds, int): cds = [cds]

    deck_count = unit.deck.count(card.id)
    if len(cds) >= deck_count:
        st.toast(f"Все копии {card.name} на перезарядке!", icon="⏳")
        return

    msg = f"💊 **{unit.name}** uses **{card.name}**!"
    item_logs = [msg]

    # [FIX] Убрали аргумент logs=None
    # target=None, так как предметы обычно применяются на себя (self)
    process_card_self_scripts("on_use", unit, None, custom_log_list=item_logs, card_override=card)

    # Накладываем кулдаун
    cooldown = max(0, card.tier - 1)
    if cooldown > 0:
        if card.id not in unit.card_cooldowns:
            unit.card_cooldowns[card.id] = []
        unit.card_cooldowns[card.id].append(cooldown)

    # Добавляем в общий лог боя для визуализации
    if 'battle_logs' not in st.session_state:
        st.session_state['battle_logs'] = []

    st.session_state['battle_logs'].append({
        "round": "Item",
        "rolls": "Consumable",
        "details": item_logs
    })


# Функция рендера инвентаря (если она нужна в этом файле)
def render_inventory(unit, unit_key):
    """
    Рендерит секцию инвентаря с предметами (CardType.ITEM).
    """
    inventory_cards = []
    if unit.deck:
        for cid in unit.deck:
            card = Library.get_card(cid)
            if card and str(card.card_type).lower() == "item":
                inventory_cards.append(card)

    if not inventory_cards:
        return

    with st.expander("🎒 Inventory (Consumables)", expanded=False):
        for card in inventory_cards:
            btn_key = f"use_item_{unit_key}_{card.id}"
            desc = card.description if card.description else "No description"

            # Кнопка использования
            if st.button(f"💊 {card.name}", key=btn_key, help=desc, width='stretch'):
                use_item_action(unit, card)
                st.rerun()