import uuid
import streamlit as st
from core.card import Card
from core.library import Library

# Импорт новых секций
from ui.editor.sections.loader import render_editor_loader
from ui.editor.sections.general import render_general_info
from ui.editor.sections.global_effects import render_global_effects
from ui.editor.sections.dice_editor import render_dice_editor

def render_editor_page():
    st.markdown("### 🛠️ Универсальный Редактор Карт")

    # Инициализация стейта
    if "ed_script_list" not in st.session_state: st.session_state["ed_script_list"] = []
    if "ed_flags" not in st.session_state: st.session_state["ed_flags"] = []
    if "ed_source_file" not in st.session_state: st.session_state["ed_source_file"] = "custom_cards.json"

    # 1. Загрузка
    render_editor_loader()

    # 2. Основная инфа
    name, tier, ctype, desc = render_general_info()

    # 3. Глобальные эффекты
    render_global_effects()

    # 4. Кубики (возвращает готовые объекты Dice)
    dice_objects = render_dice_editor(ctype)

    # 5. Сохранение и Удаление
    st.divider()
    c_save, c_del, _ = st.columns([1, 1, 2])

    if c_save.button("💾 Сохранить Карту", type="primary"):
        if not name:
            st.error("Введите имя!")
        else:
            cid = st.session_state.get("ed_loaded_id")
            if not cid:
                cid = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:4]

            # Сборка глобальных скриптов
            final_global_scripts = {}
            for gs in st.session_state["ed_script_list"]:
                trig = gs["trigger"]
                if trig not in final_global_scripts: final_global_scripts[trig] = []
                final_global_scripts[trig].append(gs["data"])

            new_card = Card(
                id=cid,
                name=name,
                tier=tier,
                card_type=ctype,
                description=desc,
                dice_list=dice_objects,
                scripts=final_global_scripts,
                flags=st.session_state["ed_flags"]
            )
            target_file = st.session_state.get("ed_source_file", "custom_cards.json")

            Library.save_card(new_card, filename=target_file)
            st.toast(f"Карта {name} сохранена в {target_file}!", icon="✅")
            st.rerun()

    if st.session_state.get("ed_loaded_id"):
        if c_del.button("🗑️ Удалить"):
            Library.delete_card(st.session_state["ed_loaded_id"])
            st.toast("Удалено!", icon="🗑️")
            from ui.editor.editor_loader import reset_editor_state
            reset_editor_state()
            st.rerun()