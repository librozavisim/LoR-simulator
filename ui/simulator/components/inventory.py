from collections import Counter

import streamlit as st

from core.library import Library


def render_inventory(unit, unit_key):
    inventory_cards = []
    if unit.deck:
        for cid in unit.deck:
            card = Library.get_card(cid)
            if card and str(card.card_type).lower() == "item":
                inventory_cards.append(card)

    deck_counts = Counter(unit.deck)

    if not inventory_cards: return

    with st.expander("🎒 Inventory (Consumables)", expanded=False):
        seen_items = set()

        for card in inventory_cards:
            if card.id in seen_items: continue
            seen_items.add(card.id)

            btn_key = f"use_item_{unit_key}_{card.id}"
            desc = card.description if card.description else "No description"

            # Логика кулдауна предметов
            cooldowns_list = unit.card_cooldowns.get(card.id, [])
            if isinstance(cooldowns_list, int): cooldowns_list = [cooldowns_list]

            copies_on_cd = len(cooldowns_list)
            total_copies = deck_counts[card.id]
            available_copies = total_copies - copies_on_cd

            if available_copies <= 0:
                max_cd = max(cooldowns_list) if cooldowns_list else 0
                st.button(
                    f"⏳ {card.name} ({max_cd})",
                    key=btn_key, disabled=True, width='stretch',
                    help=f"{desc}\n\n(Все копии на перезарядке)"
                )
            else:
                label = f"💊 {card.name}"
                if total_copies > 1:
                    label += f" ({available_copies}/{total_copies})"

                if st.button(label, key=btn_key, help=desc, width='stretch'):
                    # Отложенный импорт для избежания циклических ссылок, если логика использует компоненты
                    from ui.simulator.logic.simulator_logic import use_item_action
                    use_item_action(unit, card)
                    st.rerun()