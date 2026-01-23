import streamlit as st
from core.library import Library
from ui.editor.editor_loader import load_card_to_state

def render_editor_loader():
    """
    Отрисовывает панель выбора файла и загрузки карты.
    """
    all_cards = Library.get_all_cards()

    # 1. Получаем список всех файлов-источников
    unique_sources = set()
    for c in all_cards:
        src = Library.get_source(c.id)
        if src: unique_sources.add(src)

    sorted_sources = sorted(list(unique_sources))
    sorted_sources.insert(0, "All")

    # 2. Интерфейс выбора
    c_filter, c_card_sel, c_load_btn = st.columns([1.5, 2.5, 1])

    with c_filter:
        selected_source = st.selectbox("📁 Источник", sorted_sources, key="ed_file_filter")

    # 3. Фильтрация списка карт
    filtered_cards = []
    if selected_source == "All":
        filtered_cards = all_cards
    else:
        filtered_cards = [c for c in all_cards if Library.get_source(c.id) == selected_source]

    # Сортировка
    filtered_cards.sort(key=lambda x: (Library.get_source(x.id) or "", x.name))

    # Формирование опций
    card_options = {"(Создать новую)": None}
    for c in filtered_cards:
        src = Library.get_source(c.id)
        label = c.name
        if selected_source == "All" and src:
            label = f"[{src}] {c.name}"
        label += f" ({c.id[:4]}..)"
        card_options[label] = c

    with c_card_sel:
        selected_option = st.selectbox("Шаблон", list(card_options.keys()))

    with c_load_btn:
        st.write("")
        st.write("")
        if st.button("📥 Загрузить", width='stretch'):
            if card_options[selected_option]:
                load_card_to_state(card_options[selected_option])
            else:
                # Сброс для новой карты
                from ui.editor.editor_loader import reset_editor_state
                reset_editor_state()
            st.rerun()