
# app.py
import streamlit as st
import os
import json
import copy

from core.unit.unit import Unit
from core.unit.unit_library import UnitLibrary
from ui.cheat_sheet import render_cheat_sheet_page
from ui.checks import render_checks_page
from ui.leveling import render_leveling_page
from ui.profile.main import render_profile_page
from ui.styles import apply_styles
from ui.simulator.simulator import render_simulator_page
from ui.editor.editor import render_editor_page
from ui.tree_view import render_skill_tree_page

apply_styles()

STATE_FILE = "data/simulator_state.json"


def load_from_disk():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content: return json.loads(content)
        except Exception as e:
            print(f"Error loading: {e}")
    return {}


def save_to_disk(data):
    try:
        os.makedirs("data", exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"Error saving: {e}")


# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
if 'persistent_state' not in st.session_state:
    loaded_state = load_from_disk()
    st.session_state['persistent_state'] = loaded_state

    # 1. Восстановление навигации
    if 'nav_page' not in st.session_state:
        st.session_state['nav_page'] = loaded_state.get("page", "⚔️ Simulator")

    # 2. Восстановление селекторов
    selector_keys = {
        "profile_unit": "profile_selected_unit",
        "leveling_unit": "leveling_selected_unit",
        "tree_unit": "tree_selected_unit",
        "checks_unit": "checks_selected_unit"
    }

    # Загружаем ростер для проверки валидности ключей
    temp_roster = UnitLibrary.load_all() or {"Roland": Unit("Roland")}
    roster_keys = list(temp_roster.keys())

    for json_key, session_key in selector_keys.items():
        val = loaded_state.get(json_key)
        if val in roster_keys:
            st.session_state[session_key] = val

    # 3. ВОССТАНОВЛЕНИЕ КОМАНД (ПОЛНЫЕ ОБЪЕКТЫ)
    # Теперь мы восстанавливаем объекты из сохраненных данных, а не по именам

    # Левая команда
    left_data = loaded_state.get("team_left_data", [])
    restored_left = []
    for u_data in left_data:
        try:
            u = Unit.from_dict(u_data)
            u.recalculate_stats()  # Важно пересчитать статы после загрузки
            restored_left.append(u)
        except Exception as e:
            print(f"Error restoring unit: {e}")

    st.session_state['team_left'] = restored_left

    # Правая команда
    right_data = loaded_state.get("team_right_data", [])
    restored_right = []
    for u_data in right_data:
        try:
            u = Unit.from_dict(u_data)
            u.recalculate_stats()
            restored_right.append(u)
        except:
            pass

    st.session_state['team_right'] = restored_right


def update_and_save_state():
    """Сохраняет текущее состояние приложения в файл."""
    p_state = st.session_state.get('persistent_state', {})

    # 1. Навигация
    p_state["page"] = st.session_state.get("nav_page", "⚔️ Simulator")

    # 2. Селекторы (Профиль, Уровни и т.д.)
    # Сохраняем только если они есть в сессии
    if "profile_selected_unit" in st.session_state:
        p_state["profile_unit"] = st.session_state["profile_selected_unit"]
    if "leveling_selected_unit" in st.session_state:
        p_state["leveling_unit"] = st.session_state["leveling_selected_unit"]
    if "tree_selected_unit" in st.session_state:
        p_state["tree_unit"] = st.session_state["tree_selected_unit"]
    if "checks_selected_unit" in st.session_state:
        p_state["checks_unit"] = st.session_state["checks_selected_unit"]

    # 3. КОМАНДЫ СИМУЛЯТОРА (СЕРИАЛИЗАЦИЯ)
    # Сохраняем полные данные юнитов, включая их текущие HP/SP
    # Это позволяет сохранять "шаблонных" персонажей (клонов)

    if "team_left" in st.session_state:
        p_state["team_left_data"] = [u.to_dict() for u in st.session_state["team_left"]]
    else:
        p_state["team_left_data"] = []

    if "team_right" in st.session_state:
        p_state["team_right_data"] = [u.to_dict() for u in st.session_state["team_right"]]
    else:
        p_state["team_right_data"] = []

    st.session_state['persistent_state'] = p_state
    save_to_disk(p_state)


if 'save_callback' not in st.session_state:
    st.session_state['save_callback'] = update_and_save_state

if 'roster' not in st.session_state:
    st.session_state['roster'] = UnitLibrary.load_all() or {"Roland": Unit("Roland")}

roster_keys = sorted(list(st.session_state['roster'].keys()))
if not roster_keys: st.stop()

# --- ГЛОБАЛЬНЫЕ ОБЪЕКТЫ (Инициализация пустых, если не загрузились) ---
if 'team_left' not in st.session_state: st.session_state['team_left'] = []
if 'team_right' not in st.session_state: st.session_state['team_right'] = []
if 'battle_logs' not in st.session_state: st.session_state['battle_logs'] = []
if 'script_logs' not in st.session_state: st.session_state['script_logs'] = ""

# --- ОТРИСОВКА ---
st.sidebar.title("Navigation")

# Список страниц (включая новую Cheat Sheet)
pages = ["⚔️ Simulator", "👤 Profile", "🌳 Skill Tree", "📈 Leveling", "🛠️ Card Editor", "🎲 Checks", "📚 Cheat Sheet"]

page = st.sidebar.radio("Go to", pages, key="nav_page", on_change=update_and_save_state)

# === СТРАНИЦА: SIMULATOR ===
if "Simulator" in page:
    st.sidebar.divider()
    st.sidebar.subheader("⚔️ Team Builder")

    # Проверка фазы боя
    current_phase = st.session_state.get('phase', 'roll')
    is_team_locked = current_phase != 'roll'

    if is_team_locked:
        st.sidebar.info("🔒 Идет бой. Изменение команд заблокировано.")

    # 1. Выбор юнита
    unit_to_add_name = st.sidebar.selectbox(
        "Выберите персонажа",
        roster_keys,
        key="sim_unit_add_sel",
        disabled=is_team_locked
    )

    # Чекбокс режима
    as_template = st.sidebar.checkbox(
        "Добавить как копию (Шаблон)",
        value=False,
        help="Если включено: создает независимую копию. Если выключено: добавляет ссылку на оригинал.",
        disabled=is_team_locked
    )


    # Функция добавления
    def add_unit_to_team(target_list_key):
        if not unit_to_add_name: return

        # Получаем оригинал из ростера
        base_unit = st.session_state['roster'][unit_to_add_name]

        unit_to_add = None

        if as_template:
            # === РЕЖИМ ШАБЛОНА (КОПИЯ) ===
            unit_to_add = copy.deepcopy(base_unit)

            # Даем уникальное имя (Крыса 1, Крыса 2...)
            existing_names = [u.name for u in st.session_state['team_left'] + st.session_state['team_right']]
            count = 0
            for name in existing_names:
                if name.startswith(base_unit.name):
                    count += 1

            if count > 0:
                unit_to_add.name = f"{base_unit.name} {count + 1}"

        else:
            # === РЕЖИМ ОРИГИНАЛА (ССЫЛКА) ===
            # Проверяем, нет ли его уже в бою
            all_current_units = st.session_state['team_left'] + st.session_state['team_right']
            if any(u is base_unit for u in all_current_units):
                st.sidebar.error(f"❌ {base_unit.name} уже в команде! (Используйте режим копии для дублей)")
                return

            unit_to_add = base_unit  # Передаем ссылку!

        # === СОХРАНЯЕМ СНИМОК СОСТОЯНИЯ (Для Reset Battle) ===
        unit_to_add.memory['start_of_battle_stats'] = {
            'hp': unit_to_add.current_hp,
            'sp': unit_to_add.current_sp,
            'stagger': unit_to_add.current_stagger
        }

        st.session_state[target_list_key].append(unit_to_add)
        st.session_state['battle_logs'] = []  # Сброс логов

        # Сохраняем изменения на диск
        update_and_save_state()


    # 2. Кнопки
    c_add_l, c_add_r = st.sidebar.columns(2)

    if c_add_l.button("⬅️ Add Left", use_container_width=True, disabled=is_team_locked):
        add_unit_to_team('team_left')
        st.rerun()

    if c_add_r.button("Add Right ➡️", use_container_width=True, disabled=is_team_locked):
        add_unit_to_team('team_right')
        st.rerun()

    # 3. Списки команд с удалением
    st.sidebar.markdown("---")


    # Функция удаления
    def remove_unit(team_key, idx):
        st.session_state[team_key].pop(idx)
        update_and_save_state()
        st.rerun()


    # --- LEFT TEAM ---
    st.sidebar.markdown(f"**Left Team ({len(st.session_state['team_left'])})**")
    if st.session_state['team_left']:
        for i, u in enumerate(st.session_state['team_left']):
            c_name, c_del = st.sidebar.columns([4, 1])
            c_name.caption(f"{i + 1}. {u.name} (Lvl {u.level})")
            if c_del.button("❌", key=f"del_l_{i}", disabled=is_team_locked):
                remove_unit('team_left', i)
    else:
        st.sidebar.caption("Пусто")

    # --- RIGHT TEAM ---
    st.sidebar.markdown(f"**Right Team ({len(st.session_state['team_right'])})**")
    if st.session_state['team_right']:
        for i, u in enumerate(st.session_state['team_right']):
            c_name, c_del = st.sidebar.columns([4, 1])
            c_name.caption(f"{i + 1}. {u.name} (Lvl {u.level})")
            if c_del.button("❌", key=f"del_r_{i}", disabled=is_team_locked):
                remove_unit('team_right', i)
    else:
        st.sidebar.caption("Пусто")

    # Кнопка очистки
    if st.sidebar.button("🗑️ Очистить все команды", use_container_width=True, disabled=is_team_locked):
        st.session_state['team_left'] = []
        st.session_state['team_right'] = []
        st.session_state['battle_logs'] = []
        update_and_save_state()
        st.rerun()

    render_simulator_page()

# === ОСТАЛЬНЫЕ СТРАНИЦЫ ===
elif "Profile" in page:
    # При смене вкладки тоже можно дернуть сохранение, но on_change уже это делает
    render_profile_page()

elif "Checks" in page:
    render_checks_page()

elif "Leveling" in page:
    render_leveling_page()

elif "Skill Tree" in page:
    render_skill_tree_page()

elif "Cheat Sheet" in page:
    render_cheat_sheet_page()

else:
    render_editor_page()
