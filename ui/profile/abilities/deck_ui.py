import os
from collections import Counter

import streamlit as st

from core.library import Library
from ui.profile.abilities.build_manager import (
    BUILDS_DIR, ensure_builds_dir, save_build, load_build_ids,
    get_card_source_files, load_ids_from_source, force_update_deck_ui
)


def render_deck_builder(unit, u_key):
    # Предварительная загрузка библиотеки
    all_library_cards = Library.get_all_cards()
    all_library_cards.sort(key=lambda x: (x.tier, x.name))

    card_map = {c.id: c for c in all_library_cards}
    all_card_ids = [c.id for c in all_library_cards]

    st.subheader("🃏 Боевая колода")

    # --- УПРАВЛЕНИЕ СБОРКАМИ ---
    with st.expander("📁 Управление сборками (Сохранить / Загрузить)", expanded=False):
        c_save, c_load = st.columns(2)

        # 1. Сохранение
        with c_save:
            st.markdown("**:floppy_disk: Сохранить текущую**")
            build_name = st.text_input("Название сборки", placeholder="Например: Лима_Снайпер", key=f"bn_{u_key}")
            if st.button("Сохранить", key=f"btn_save_{u_key}"):
                if build_name and unit.deck:
                    save_build(build_name, unit.deck)
                elif not unit.deck:
                    st.warning("Колода пуста!")
                else:
                    st.warning("Введите имя сборки!")

        # 2. Загрузка
        with c_load:
            st.markdown("**:open_file_folder: Загрузить**")
            ensure_builds_dir()
            saved_builds = [f for f in os.listdir(BUILDS_DIR) if f.endswith(".json")]

            tab_saved, tab_source = st.tabs(["Свои сборки", "Из файлов игры"])

            with tab_saved:
                if saved_builds:
                    sel_build = st.selectbox("Выберите файл", saved_builds, key=f"sel_bld_{u_key}")
                    if st.button("Загрузить сборку", key=f"btn_load_{u_key}"):
                        loaded_ids = load_build_ids(sel_build)
                        if loaded_ids:
                            final_ids = force_update_deck_ui(u_key, loaded_ids, all_card_ids)
                            unit.deck = final_ids
                            st.success(f"Загружено {len(final_ids)} карт!")
                            st.rerun()
                else:
                    st.caption("Нет сохраненных сборок")

            with tab_source:
                sources = get_card_source_files()
                if sources:
                    sel_source = st.selectbox("Выберите файл", sources, key=f"sel_src_{u_key}")
                    if st.button("📥 Взять ВСЕ карты", key=f"btn_src_{u_key}"):
                        loaded_ids = load_ids_from_source(sel_source)
                        if loaded_ids:
                            final_ids = force_update_deck_ui(u_key, loaded_ids, all_card_ids)
                            unit.deck = final_ids
                            st.success(f"Добавлено {len(final_ids)} карт!")
                            st.rerun()
                else:
                    st.caption("Нет файлов")

    st.markdown("---")

    # --- ВЫБОР КАРТ ---
    current_counts = Counter(unit.deck)
    valid_unique_ids = [cid for cid in current_counts.keys() if cid in card_map]

    selected_unique_ids = st.multiselect(
        "Редактор колоды (выбор карт):",
        options=all_card_ids,
        default=valid_unique_ids,
        format_func=lambda x: f"{card_map[x].name} [{card_map[x].tier}]" if x in card_map else x,
        key=f"deck_sel_{u_key}"
    )

    new_deck_list = []
    if selected_unique_ids:
        st.caption("Количество копий (x1 - x3):")
        cols = st.columns(3)

        for idx, cid in enumerate(selected_unique_ids):
            card_obj = card_map.get(cid)
            if not card_obj: continue

            col = cols[idx % 3]
            with col:
                default_qty = current_counts[cid] if current_counts[cid] > 0 else 1
                qty = st.number_input(
                    f"{card_obj.name}",
                    min_value=1, max_value=3,
                    value=default_qty,
                    key=f"qty_{u_key}_{cid}"
                )
                new_deck_list.extend([cid] * qty)

    # Применение изменений
    if sorted(unit.deck) != sorted(new_deck_list):
        unit.deck = new_deck_list

    count_color = "green" if len(unit.deck) == 9 else "red"
    st.markdown(f"**Всего карт: :{count_color}[{len(unit.deck)}]** / 9")
    st.markdown("---")