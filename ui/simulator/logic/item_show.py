import streamlit as st

from core.library import Library


def use_item_action(unit, card):
    # Проверка наличия доступных копий (дублирует UI, но для надежности)
    cds = unit.card_cooldowns.get(card.id, [])
    if isinstance(cds, int): cds = [cds]

    deck_count = unit.deck.count(card.id)
    if len(cds) >= deck_count:
        st.toast(f"Все копии {card.name} на перезарядке!", icon="⏳")
        return

    msg = f"💊 **{unit.name}** uses **{card.name}**!"
    item_logs = [msg]

    # Используем process_card_self_scripts, передавая item_logs как custom_log_list
    # target=None, так как предметы обычно на себя (self). Если нужен таргет, придется усложнять UI.
    # Пока считаем, что таблетки пьют сами.
    from logic.mechanics.scripts import process_card_self_scripts
    process_card_self_scripts("on_use", unit, None, logs=None, custom_log_list=item_logs, card_override=card)

    cooldown = max(0, card.tier - 1)
    if cooldown > 0:
        if card.id not in unit.card_cooldowns:
            unit.card_cooldowns[card.id] = []
        # Добавляем 1 инстанс кулдауна
        unit.card_cooldowns[card.id].append(cooldown)
        # Можно добавить лог про кд, если нужно, но обычно это визуально видно
        # item_logs.append(f"(Cooldown: {cooldown})")
    # Добавляем в общий лог боя
    st.session_state['battle_logs'].append({
        "round": "Item",
        "rolls": "Consumable",
        "details": item_logs
    })

def render_inventory(unit, unit_key):
    """
    Рендерит секцию инвентаря с предметами (CardType.ITEM).
    """
    # Фильтруем карты в колоде, оставляя только предметы
    inventory_cards = []
    if unit.deck:
        for cid in unit.deck:
            card = Library.get_card(cid)
            # Проверяем тип
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
                from ui.simulator.logic.simulator_logic import use_item_action
                use_item_action(unit, card)
                st.rerun()