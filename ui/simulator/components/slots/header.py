from ui.simulator.components.common import CARD_TYPE_ICONS


def render_slot_header(slot, slot_idx):
    """
    Формирует текстовый заголовок для Expander'а.
    """
    speed = slot['speed']
    ui_stat = slot.get('ui_status', {"text": "...", "icon": "", "color": "gray"})
    selected_card = slot.get('card')

    if selected_card:
        c_type_lower = str(selected_card.card_type).lower()
        type_emoji = "📄"
        for k, v in CARD_TYPE_ICONS.items():
            if k in c_type_lower:
                type_emoji = v
                break
        card_name_header = f"[{selected_card.tier}] {type_emoji} {selected_card.name}"
    else:
        card_name_header = "⛔ Пусто"

    spd_label = f"🎲{speed}"
    if slot.get("source_effect"):
        spd_label += f" ({slot.get('source_effect')})"

    lock_icon = "🔒 " if slot.get('locked') else ""

    return f"{lock_icon}S{slot_idx + 1} ({spd_label}) | {ui_stat['icon']} {ui_stat['text']} | {card_name_header}"