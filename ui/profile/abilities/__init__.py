from ui.profile.abilities.deck_ui import render_deck_builder
from ui.profile.abilities.talents_ui import render_talents_ui

def render_abilities(unit, u_key):
    """
    Главная функция отрисовки вкладки Способностей.
    Собирает компоненты колоды и талантов.
    """
    render_deck_builder(unit, u_key)
    render_talents_ui(unit, u_key)