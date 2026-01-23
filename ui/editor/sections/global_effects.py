import streamlit as st
from ui.editor.config import SCRIPT_SCHEMAS
from ui.editor.forms import render_dynamic_form
from ui.editor.callbacks import edit_global_script, delete_global_script
from ui.components import _format_script_text

def render_global_effects():
    """
    Отрисовывает редактор глобальных скриптов карты (On Use и т.д.).
    """
    with st.expander("✨ Эффекты карты (Global Scripts)", expanded=True):
        ce_col1, ce_col2 = st.columns([1, 2])
        ce_trigger = ce_col1.selectbox("Триггер", ["on_use", "on_combat_end"], key="ce_trig")
        ce_schema_name = ce_col2.selectbox("Эффект", list(SCRIPT_SCHEMAS.keys()), key="ce_schema")

        current_params = render_dynamic_form("global", ce_schema_name)

        if st.button("➕ Добавить эффект карты"):
            script_id = SCRIPT_SCHEMAS[ce_schema_name]["id"]
            st.session_state["ed_script_list"].append({
                "trigger": ce_trigger,
                "data": {"script_id": script_id, "params": current_params}
            })
            st.rerun()

        st.divider()
        st.caption("Список эффектов карты:")
        g_scripts = st.session_state["ed_script_list"]

        if not g_scripts:
            st.caption("Пусто")

        for i, item in enumerate(g_scripts):
            trig = item['trigger']
            sid = item['data'].get('script_id')
            p = item['data'].get('params', {})

            c_txt, c_edit, c_del = st.columns([4, 0.5, 0.5])
            c_txt.markdown(f"`{trig}` : **{_format_script_text(sid, p)}**", unsafe_allow_html=True)

            c_edit.button("✏️", key=f"edit_g_{i}", on_click=edit_global_script, args=(i,), help="Редактировать")
            c_del.button("❌", key=f"del_g_{i}", on_click=delete_global_script, args=(i,), help="Удалить")