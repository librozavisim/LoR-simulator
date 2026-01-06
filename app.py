# app.py
import streamlit as st
import os
import json

from core.unit.unit import Unit
from core.unit.unit_library import UnitLibrary
from ui.checks import render_checks_page
from ui.leveling import render_leveling_page
from ui.profile.main import render_profile_page
from ui.styles import apply_styles
from ui.simulator.simulator import render_simulator_page
from ui.editor.editor import render_editor_page
from ui.tree_view import render_skill_tree_page

# Применяем CSS и конфиг
apply_styles()

# --- STATE MANAGEMENT (Умное сохранение) ---
STATE_FILE = "data/simulator_state.json"


def load_app_state():
    """Загружает все состояние приложения как словарь."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
    return {}


def save_app_state():
    """
    Сохраняет состояние.
    ВАЖНО: Сначала читает файл, чтобы не затереть данные со скрытых страниц.
    Обновляет только те поля, которые сейчас активны (есть в session_state).
    """
    # 1. Читаем текущий файл
    current_data = load_app_state()

    # 2. Обновляем текущую страницу (она всегда активна)
    current_data["page"] = st.session_state.get("nav_page", "⚔️ Simulator")

    # 3. Обновляем КОМАНДЫ (Только если мы на странице симулятора и ключи есть)
    if "team_left_names" in st.session_state:
        current_data["left"] = st.session_state["team_left_names"]

    if "team_right_names" in st.session_state:
        current_data["right"] = st.session_state["team_right_names"]

    # 4. Обновляем данные ВКЛАДОК (Только если ключ есть в сессии, т.е. виджет активен)
    if "profile_selected_unit" in st.session_state:
        current_data["profile_unit"] = st.session_state["profile_selected_unit"]

    if "leveling_selected_unit" in st.session_state:
        current_data["leveling_unit"] = st.session_state["leveling_selected_unit"]

    if "tree_selected_unit" in st.session_state:
        current_data["tree_unit"] = st.session_state["tree_selected_unit"]

    if "checks_selected_unit" in st.session_state:
        current_data["checks_unit"] = st.session_state["checks_selected_unit"]

    # 5. Записываем обратно
    try:
        os.makedirs("data", exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving state: {e}")


# Кладем функцию в сессию для вызова из других файлов
if 'save_callback' not in st.session_state:
    st.session_state['save_callback'] = save_app_state

# --- INIT ROSTER ---
if 'roster' not in st.session_state:
    loaded_roster = UnitLibrary.load_all()
    # Создаем тестового, если пусто
    if not loaded_roster:
        roland = Unit("Roland")
        roland.attributes["endurance"] = 5
        roland.attributes["strength"] = 5
        roland.base_hp = 75
        roland.recalculate_stats()
        roland.current_hp = roland.max_hp
        roland.current_sp = roland.max_sp
        UnitLibrary.save_unit(roland)
        loaded_roster = UnitLibrary.load_all()
    st.session_state['roster'] = loaded_roster

roster_keys = list(st.session_state['roster'].keys())
if not roster_keys:
    st.error("Roster is empty!")
    st.stop()

# --- ВОССТАНОВЛЕНИЕ СОСТОЯНИЯ (Каждый запуск) ---
# Мы делаем это при каждом реране, чтобы восстановить значения виджетов перед их отрисовкой
saved_data = load_app_state()

# 1. Восстанавливаем страницу навигации
if 'nav_page' not in st.session_state:
    st.session_state['nav_page'] = saved_data.get("page", "⚔️ Simulator")

# 2. Восстанавливаем Команды (если их нет в сессии)
if 'team_left_names' not in st.session_state:
    s_left = saved_data.get("left", [])
    s_right = saved_data.get("right", [])
    # Валидация (вдруг персонажа удалили)
    valid_left = [n for n in s_left if n in roster_keys]
    valid_right = [n for n in s_right if n in roster_keys]

    st.session_state['team_left_names'] = valid_left if valid_left else [roster_keys[0]]
    st.session_state['team_right_names'] = valid_right if valid_right else [
        roster_keys[-1] if len(roster_keys) > 1 else roster_keys[0]]


# 3. Функция для восстановления выбора на вкладках
def restore_key(session_key, json_key):
    # Если ключа нет в сессии (мы только пришли на страницу), но он есть в файле -> восстанавливаем
    if session_key not in st.session_state and json_key in saved_data:
        val = saved_data[json_key]
        if val in roster_keys:
            st.session_state[session_key] = val


# Пытаемся восстановить все ключи.
# Streamlit примет их, если виджет с таким key будет отрисован на текущей странице.
restore_key("profile_selected_unit", "profile_unit")
restore_key("leveling_selected_unit", "leveling_unit")
restore_key("tree_selected_unit", "tree_unit")
restore_key("checks_selected_unit", "checks_unit")

# --- ОБЪЕКТЫ И ЛОГИ ---
if 'team_left' not in st.session_state: st.session_state['team_left'] = []
if 'team_right' not in st.session_state: st.session_state['team_right'] = []
if 'battle_logs' not in st.session_state: st.session_state['battle_logs'] = []
if 'script_logs' not in st.session_state: st.session_state['script_logs'] = ""
if 'turn_message' not in st.session_state: st.session_state['turn_message'] = ""

# --- NAVIGATION ---
st.sidebar.title("Navigation")

# on_change=save_app_state сохранит страницу при переключении
page = st.sidebar.radio(
    "Go to",
    ["⚔️ Simulator", "👤 Profile", "🌳 Skill Tree", "📈 Leveling", "🛠️ Card Editor", "🎲 Checks"],
    key="nav_page",
    on_change=save_app_state
)

if "Simulator" in page:
    st.sidebar.divider()
    st.sidebar.markdown("**Team Setup**")

    # Виджеты существуют только здесь, поэтому ключи team_left_names есть только здесь
    left_sel = st.sidebar.multiselect("Left Team", roster_keys, key="team_left_names")
    right_sel = st.sidebar.multiselect("Right Team", roster_keys, key="team_right_names")

    if st.sidebar.button("Apply Teams", type="primary"):
        st.session_state['team_left'] = [st.session_state['roster'][n] for n in left_sel]
        st.session_state['team_right'] = [st.session_state['roster'][n] for n in right_sel]
        st.session_state['battle_logs'] = []
        save_app_state()
        st.rerun()

    # Инициализация объектов, если пусто (первый запуск)
    if not st.session_state['team_left'] and left_sel:
        st.session_state['team_left'] = [st.session_state['roster'][n] for n in left_sel]
    if not st.session_state['team_right'] and right_sel:
        st.session_state['team_right'] = [st.session_state['roster'][n] for n in right_sel]

    # Совместимость для старых функций
    if st.session_state['team_left']: st.session_state['attacker'] = st.session_state['team_left'][0]
    if st.session_state['team_right']: st.session_state['defender'] = st.session_state['team_right'][0]

    render_simulator_page()

elif "Profile" in page:
    render_profile_page()
elif "Checks" in page:
    render_checks_page()
elif "Leveling" in page:
    render_leveling_page()
elif "Skill Tree" in page:
    render_skill_tree_page()
else:
    render_editor_page()