import streamlit as st
import os

from core.ranks import RANK_THRESHOLDS
from core.unit.unit import Unit
from core.unit.unit_library import UnitLibrary
from core.game_templates import CHARACTER_TEMPLATES

def save_avatar_file(uploaded, unit_name):
    os.makedirs("data/avatars", exist_ok=True)
    safe = "".join(c for c in unit_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
    path = f"data/avatars/{safe}.{uploaded.name.split('.')[-1]}"
    with open(path, "wb") as f: f.write(uploaded.getbuffer())
    return path


def create_character_from_template(template, roster):
    """Создает персонажа на основе шаблона"""
    base_name = template["name"]
    name = f"{base_name} {len(roster) + 1}"

    u = Unit(name)
    u.level = template["level"]
    u.rank = 9 - template["tier"]  # В системе рангов: 9=Rank9, 0=Color. Инверсия для UI.
    if u.rank < -1: u.rank = -1  # Cap for high tiers

    # Атрибуты из шаблона
    u.attributes["endurance"] = template["endurance"]
    u.attributes["agility"] = template["agility"]
    u.skills["speed"] = template["speed_skill"]

    # Для баланса заполняем остальные статы средними значениями
    avg_stat = template["endurance"] // 2
    u.attributes["strength"] = avg_stat
    u.skills["strike_power"] = avg_stat
    u.skills["tough_skin"] = template["endurance"] // 2

    for lvl in range(3, u.level + 1, 3):
        u.level_rolls[str(lvl)] = {"hp": 3, "sp": 3}

    u.recalculate_stats()
    return u, name


def delete_unit_action(unit_name):
    """Callback для безопасного удаления персонажа."""
    if UnitLibrary.delete_unit(unit_name):
        roster = UnitLibrary.get_roster()
        current_keys = sorted(list(roster.keys()))
        if current_keys:
            st.session_state["profile_selected_unit"] = current_keys[0]
        else:
            st.session_state["profile_selected_unit"] = None

        st.toast(f"Персонаж {unit_name} удален.", icon="🗑️")
        if 'save_callback' in st.session_state:
            st.session_state['save_callback']()


def render_header(roster):
    # --- HEADER / SELECTION ---
    c1, c2 = st.columns([3, 1])

    # === КНОПКА СОЗДАНИЯ (POPOVER) ===
    with c2.popover("➕ Создать", use_container_width=True):
        st.markdown("**Выберите шаблон:**")

        if st.button("Крыса (Пустой)", use_container_width=True):
            n = f"Unit_{len(roster) + 1}"
            u = Unit(n)
            roster[n] = u
            UnitLibrary.save_unit(u)
            st.session_state["profile_selected_unit"] = n
            if 'save_callback' in st.session_state: st.session_state['save_callback']()
            st.rerun()

        st.divider()

        for tmpl in CHARACTER_TEMPLATES:
            if tmpl["tier"] == 0: continue
            label = f"{tmpl['name']} (Lvl {tmpl['level']})"
            if st.button(label, key=f"create_{tmpl['tier']}", use_container_width=True):
                u, n = create_character_from_template(tmpl, roster)
                roster[n] = u
                UnitLibrary.save_unit(u)
                st.session_state["profile_selected_unit"] = n
                if 'save_callback' in st.session_state: st.session_state['save_callback']()
                st.rerun()

    # === [FIX] ЯВНОЕ ЗАДАНИЕ ИНДЕКСА ДЛЯ SELECTBOX ===
    # 1. Получаем список ключей
    roster_keys = sorted(list(roster.keys()))

    # 2. Получаем текущее значение из стейта (которое мы восстановили в app.py)
    current_key = st.session_state.get("profile_selected_unit")

    # 3. Вычисляем индекс для UI
    default_index = 0
    if current_key in roster_keys:
        default_index = roster_keys.index(current_key)

    # 4. Рисуем виджет с index
    sel = c1.selectbox(
        "Персонаж",
        roster_keys,
        index=default_index,  # <--- Ключевое изменение
        key="profile_selected_unit",
        on_change=st.session_state.get('save_callback')
    )

    unit = roster[sel]
    u_key = unit.name.replace(" ", "_")

    c_save, c_del = st.columns([4, 1])

    with c_save:
        if st.button("💾 СОХРАНИТЬ ПРОФИЛЬ", type="primary", use_container_width=True, key=f"save_btn_{u_key}"):
            UnitLibrary.save_unit(unit)
            st.toast("Данные персонажа сохранены!", icon="✅")

    with c_del:
        with st.popover("🗑️", use_container_width=True):
            st.warning(f"Удалить {unit.name}?")
            st.button(
                "Да, удалить",
                type="primary",
                key=f"del_confirm_{u_key}",
                on_click=delete_unit_action,
                args=(unit.name,)
            )

    st.divider()
    return unit, u_key
def render_basic_info(unit, u_key):
    # Avatar
    img = unit.avatar if unit.avatar and os.path.exists(
        unit.avatar) else "https://placehold.co/150x150/png?text=No+Image"
    st.image(img, width='stretch')
    upl = st.file_uploader("Загрузить арт", type=['png', 'jpg'], label_visibility="collapsed", key=f"upl_{u_key}")
    if upl:
        unit.avatar = save_avatar_file(upl, unit.name)
        UnitLibrary.save_unit(unit)
        st.rerun()

    # Basic Data
    unit.name = st.text_input("Имя", unit.name, key=f"name_{u_key}")

    c_lvl, c_int = st.columns(2)
    unit.level = c_lvl.number_input("Уровень", 1, 120, unit.level, key=f"lvl_{u_key}")

    # Интеллект
    new_int = c_int.number_input("Баз. Инт.", 1, 30, unit.base_intellect, key=f"base_int_{u_key}")
    if new_int != unit.base_intellect:
        unit.base_intellect = new_int
        unit.recalculate_stats()
        st.rerun()

    total_int_data = unit.modifiers.get("total_intellect", {})
    if isinstance(total_int_data, dict):
        total_int = total_int_data.get("flat", unit.base_intellect)
    else:
        total_int = total_int_data if total_int_data else unit.base_intellect

    if total_int > unit.base_intellect:
        st.info(f"🧠 Интеллект: **{total_int}** (+{total_int - unit.base_intellect})")
    else:
        st.info(f"🧠 Интеллект: **{total_int}**")

    st.divider()

    # === RANK (Ранг) ===
    st.markdown("**Ранг Фиксера**")
    r_c1, r_c2 = st.columns(2)

    unit.rank = r_c1.number_input("Текущий (Tier)", -5, 10, unit.rank, help="Официальный ранг (0-11)",
                                  key=f"rank_cur_{u_key}")

    rank_name = "Неизвестный ранг"
    rank_color = "gray"

    for _, name, tier in RANK_THRESHOLDS:
        if (10-tier) == unit.rank:
            rank_name = name
            if tier >= 10:
                rank_color = "red"
            elif tier >= 9:
                rank_color = "orange"
            elif tier >= 7:
                rank_color = "blue"
            else:
                rank_color = "green"
            break

    r_c1.markdown(f":{rank_color}[**{rank_name}**]")

    status_rank = unit.memory.get("status_rank", "9 (Fixer)")
    new_status = r_c2.text_input("Статус (Текст)", status_rank, help="Ранг репутации (текстовое описание)",
                                 key=f"rank_stat_{u_key}")
    unit.memory["status_rank"] = new_status

    st.divider()

    st.markdown(f"**🧊 Скорость:**")
    if unit.computed_speed_dice:
        for d in unit.computed_speed_dice:
            st.markdown(f"- {d[0]}~{d[1]}")
    else:
        st.markdown(f"- {unit.base_speed_min}~{unit.base_speed_max}")

    st.divider()

    with st.expander("📝 Биография и Заметки", expanded=False):
        unit.biography = st.text_area(
            "История персонажа",
            value=unit.biography,
            height=300,
            key=f"bio_{u_key}",
            help="Сюда можно писать квенту, инвентарь (мелочевку) или заметки."
        )