import os
import json
import streamlit as st
from collections import Counter
from core.library import Library
from logic.character_changing.passives import PASSIVE_REGISTRY
from logic.character_changing.talents import TALENT_REGISTRY

BUILDS_DIR = "data/builds"


def ensure_builds_dir():
    if not os.path.exists(BUILDS_DIR):
        os.makedirs(BUILDS_DIR)


def save_build(name, deck_ids):
    ensure_builds_dir()
    path = os.path.join(BUILDS_DIR, f"{name}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(deck_ids, f, indent=2, ensure_ascii=False)
        st.success(f"Сборка '{name}' успешно сохранена!")
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")


def load_build_ids(filename):
    path = os.path.join(BUILDS_DIR, filename)
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return []


def get_card_source_files():
    """Возвращает список файлов .json из папки data/cards"""
    path = "data/cards"
    if not os.path.exists(path): return []
    return sorted([f for f in os.listdir(path) if f.endswith(".json")])


def load_ids_from_source(filename):
    """Извлекает ID всех карт из файла источника"""
    path = os.path.join("data/cards", filename)
    ids = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Формат может быть { "cards": [...] } или просто [...]
            cards = data.get("cards", []) if isinstance(data, dict) else data

            if isinstance(cards, list):
                for c in cards:
                    if isinstance(c, dict) and "id" in c:
                        ids.append(c["id"])
    except Exception as e:
        st.error(f"Ошибка чтения файла источника: {e}")
    return ids


def force_update_deck_ui(u_key, new_deck_ids, all_valid_ids):
    """
    Принудительно обновляет состояние виджетов Streamlit,
    чтобы они отобразили новую загруженную колоду, а не старое состояние.
    """
    # 1. Фильтруем только валидные ID (которые есть в библиотеке)
    valid_new_ids = [cid for cid in new_deck_ids if cid in all_valid_ids]

    # 2. Обновляем Multiselect
    # Удаляем дубликаты для мультиселекта
    unique_ids = list(set(valid_new_ids))
    st.session_state[f"deck_sel_{u_key}"] = unique_ids

    # 3. Обновляем Number Inputs (количества)
    counts = Counter(valid_new_ids)
    for cid, qty in counts.items():
        # Ограничиваем кол-во (макс 3, мин 1)
        safe_qty = max(1, min(3, qty))
        st.session_state[f"qty_{u_key}_{cid}"] = safe_qty

    return valid_new_ids


def render_abilities(unit, u_key):
    # Предварительная загрузка библиотеки для проверок
    all_library_cards = Library.get_all_cards()
    all_library_cards.sort(key=lambda x: (x.tier, x.name))

    card_map = {c.id: c for c in all_library_cards}
    all_card_ids = [c.id for c in all_library_cards]  # Список допустимых ID

    # === DECK HEADER ===
    st.subheader("🃏 Боевая колода")

    # --- [NEW] УПРАВЛЕНИЕ СБОРКАМИ ---
    with st.expander("📁 Управление сборками (Сохранить / Загрузить / Из папки)", expanded=False):
        c_save, c_load = st.columns(2)

        # 1. Сохранение
        with c_save:
            st.markdown("**:floppy_disk: Сохранить текущую**")
            build_name = st.text_input("Название сборки", placeholder="Например: Лима_Снайпер", key=f"bn_{u_key}")
            if st.button("Сохранить", key=f"btn_save_{u_key}"):
                if build_name and unit.deck:
                    save_build(build_name, unit.deck)
                elif not unit.deck:
                    st.warning("Колода пуста, нечего сохранять!")
                else:
                    st.warning("Введите имя сборки!")

        # 2. Загрузка
        with c_load:
            st.markdown("**:open_file_folder: Загрузить**")
            ensure_builds_dir()
            saved_builds = [f for f in os.listdir(BUILDS_DIR) if f.endswith(".json")]

            # Вкладки для типа загрузки
            tab_saved, tab_source = st.tabs(["Свои сборки", "Из файлов игры"])

            with tab_saved:
                if saved_builds:
                    sel_build = st.selectbox("Выберите файл", saved_builds, key=f"sel_bld_{u_key}")
                    if st.button("Загрузить сборку", key=f"btn_load_{u_key}"):
                        loaded_ids = load_build_ids(sel_build)
                        if loaded_ids:
                            # [FIX] Принудительное обновление UI
                            final_ids = force_update_deck_ui(u_key, loaded_ids, all_card_ids)
                            unit.deck = final_ids
                            st.success(f"Загружено {len(final_ids)} карт!")
                            st.rerun()
                else:
                    st.caption("Нет сохраненных сборок")

            with tab_source:
                sources = get_card_source_files()
                if sources:
                    sel_source = st.selectbox("Выберите файл с картами", sources, key=f"sel_src_{u_key}")
                    if st.button("📥 Взять ВСЕ карты из файла", key=f"btn_src_{u_key}",
                                 help="Заменит текущую колоду всеми картами из выбранного файла"):
                        loaded_ids = load_ids_from_source(sel_source)
                        if loaded_ids:
                            # [FIX] Принудительное обновление UI
                            final_ids = force_update_deck_ui(u_key, loaded_ids, all_card_ids)
                            unit.deck = final_ids
                            st.success(f"Добавлено {len(final_ids)} карт из {sel_source}!")
                            st.rerun()
                else:
                    st.caption("Папка data/cards пуста")

    st.markdown("---")
    # -----------------------------------

    # 1. Считаем текущее количество
    current_counts = Counter(unit.deck)

    # Валидация ID (чтобы не упало, если карта удалена)
    valid_unique_ids = [cid for cid in current_counts.keys() if cid in card_map]

    # 2. Мультиселект
    # Важно: default используется только при первой отрисовке.
    # Если мы не обновили st.session_state в force_update_deck_ui, то здесь останется старое значение.
    selected_unique_ids = st.multiselect(
        "Редактор колоды (выбор карт):",
        options=all_card_ids,
        default=valid_unique_ids,
        format_func=lambda x: f"{card_map[x].name} [{card_map[x].tier}]" if x in card_map else x,
        key=f"deck_sel_{u_key}"
    )

    # 3. Настройка количества
    new_deck_list = []

    if selected_unique_ids:
        st.caption("Количество копий (x1 - x3):")
        cols = st.columns(3)

        for idx, cid in enumerate(selected_unique_ids):
            card_obj = card_map.get(cid)
            if not card_obj: continue

            col = cols[idx % 3]
            with col:
                # Если мы только что загрузили деку, в session_state уже лежит правильное число из force_update_deck_ui
                # Если нет, берем из current_counts
                default_qty = current_counts[cid] if current_counts[cid] > 0 else 1

                qty = st.number_input(
                    f"{card_obj.name}",
                    min_value=1, max_value=3,
                    value=default_qty,
                    key=f"qty_{u_key}_{cid}"
                )
                new_deck_list.extend([cid] * qty)

    # 4. Применение изменений
    # Если состав изменился (пользователь покрутил ручки ИЛИ мы загрузили новую деку и обновили UI), сохраняем
    if sorted(unit.deck) != sorted(new_deck_list):
        unit.deck = new_deck_list
        # unit.recalculate_stats() # Раскомментировать если нужно пересчитывать статы от карт

    # Индикатор размера
    count_color = "green" if len(unit.deck) == 9 else "red"
    st.markdown(f"**Всего карт: :{count_color}[{len(unit.deck)}]** / 9")

    st.markdown("---")

    # === ABILITIES (Talents & Passives) ===
    st.subheader("🧬 Таланты и Пассивки")

    c_tal, c_desc = st.columns([2, 1])

    def fmt_name(aid):
        if aid in TALENT_REGISTRY: return f"★ {TALENT_REGISTRY[aid].name}"
        if aid in PASSIVE_REGISTRY: return f"🛡️ {PASSIVE_REGISTRY[aid].name}"
        return aid

    with c_tal:
        # --- TALENTS ---
        bonus_slots = int(unit.modifiers["talent_slots"]["flat"])
        max_talents = (unit.level // 3) + bonus_slots
        if max_talents < 0: max_talents = 0

        current_talents = [t for t in unit.talents if t in TALENT_REGISTRY]
        talents_key = f"mt_{u_key}"
        session_selection = st.session_state.get(talents_key, [])
        safe_limit = max(max_talents, len(current_talents), len(session_selection))

        st.markdown(f"**Таланты ({len(current_talents)} / {max_talents})**")

        if len(current_talents) > max_talents:
            st.warning(f"⚠️ Лимит превышен! Доступно: {max_talents}")

        new_talents = st.multiselect(
            "Список талантов",
            options=sorted(list(TALENT_REGISTRY.keys())),
            default=current_talents,
            format_func=fmt_name,
            max_selections=safe_limit,
            label_visibility="collapsed",
            key=talents_key
        )

        if new_talents != current_talents:
            old_unknowns = [t for t in unit.talents if t not in TALENT_REGISTRY]
            unit.talents = new_talents + old_unknowns
            unit.recalculate_stats()
            st.rerun()

        # --- PASSIVES ---
        st.markdown("**Пассивки**")
        new_passives = st.multiselect(
            "Список пассивок",
            options=sorted(list(PASSIVE_REGISTRY.keys())),
            default=[p for p in unit.passives if p in PASSIVE_REGISTRY],
            format_func=fmt_name,
            label_visibility="collapsed",
            key=f"mp_{u_key}"
        )
        if new_passives != [p for p in unit.passives if p in PASSIVE_REGISTRY]:
            old_unknowns = [p for p in unit.passives if p not in PASSIVE_REGISTRY]
            unit.passives = new_passives + old_unknowns
            unit.recalculate_stats()
            st.rerun()

    with c_desc:
        st.info("ℹ️ **Эффекты:**")
        all_ids = unit.talents + unit.passives
        if not all_ids:
            st.caption("Пусто")
        for aid in all_ids:
            obj = TALENT_REGISTRY.get(aid) or PASSIVE_REGISTRY.get(aid)
            if obj:
                with st.expander(obj.name):
                    st.write(obj.description)