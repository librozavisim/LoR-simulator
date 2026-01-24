from ui.profile.stats.attributes import render_attributes
from ui.profile.stats.augmentations import render_augmentations
from ui.profile.stats.bars import render_status_bars
from ui.profile.stats.skills import render_luck, render_skills


def render_stats(unit, u_key):
    """Главная функция для отрисовки вкладки Статистика."""
    render_augmentations(unit, u_key)
    render_status_bars(unit, u_key)
    render_attributes(unit, u_key)
    render_luck(unit, u_key)
    render_skills(unit, u_key)