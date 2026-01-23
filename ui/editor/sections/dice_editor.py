import streamlit as st
from core.dice import Dice
from core.enums import DiceType
from ui.editor.config import SCRIPT_SCHEMAS
from ui.editor.forms import render_dynamic_form
from ui.editor.callbacks import edit_dice_script, delete_dice_script
from ui.components import _format_script_text


def render_dice_editor(card_type):
    """
    Отрисовывает табы с кубиками и возвращает список объектов Dice.
    """
    st.divider()
    st.markdown("**Настройка кубиков**")

    def_dice = 0 if card_type == "Item" else 1
    if "ed_num_dice" not in st.session_state: st.session_state["ed_num_dice"] = def_dice
    num_dice = st.number_input("Кол-во кубиков", 0, 10, key="ed_num_dice")

    dice_objects = []

    if num_dice > 0:
        tabs = st.tabs([f"Dice {i + 1}" for i in range(num_dice)])

        for i, tab in enumerate(tabs):
            with tab:
                d_c1, d_c2, d_c3, d_c4 = st.columns([1.5, 1, 1, 1])
                dtype_str = d_c1.selectbox("Тип", ["Slash", "Pierce", "Blunt", "Block", "Evade"], key=f"d_t_{i}")
                d_min = d_c2.number_input("Min", -99, 999, 2, key=f"d_min_{i}")
                d_max = d_c3.number_input("Max", -99, 999, 5, key=f"d_max_{i}")
                d_counter = d_c4.checkbox("Counter?", key=f"d_cnt_{i}")

                # --- Dice Scripts ---
                st.divider()
                st.caption("Добавить эффект к кубику:")

                dice_script_key = f"ed_dice_scripts_{i}"
                if dice_script_key not in st.session_state:
                    st.session_state[dice_script_key] = []

                de_c1, de_c2 = st.columns([1, 2])
                de_trig = de_c1.selectbox("Условие", ["on_hit", "on_clash_win", "on_clash_lose", "on_roll", "on_play"],
                                          key=f"de_trig_sel_{i}")
                de_schema = de_c2.selectbox("Эффект", list(SCRIPT_SCHEMAS.keys()), key=f"de_schema_sel_{i}")

                de_params = render_dynamic_form(f"dice_{i}", de_schema)

                if st.button(f"➕ Добавить к Dice {i + 1}", key=f"add_de_{i}"):
                    s_id = SCRIPT_SCHEMAS[de_schema]["id"]
                    st.session_state[dice_script_key].append({
                        "trigger": de_trig,
                        "data": {"script_id": s_id, "params": de_params}
                    })
                    st.rerun()

                st.caption("Эффекты кубика:")
                d_scripts_list = st.session_state[dice_script_key]
                if not d_scripts_list: st.caption("Нет")

                final_dice_scripts_dict = {}

                for idx, ds in enumerate(d_scripts_list):
                    t = ds['trigger']
                    d_sid = ds['data'].get('script_id')
                    d_p = ds['data'].get('params', {})

                    c_d_txt, c_d_edit, c_d_del = st.columns([4, 0.5, 0.5])
                    c_d_txt.markdown(f"- `{t}` : {_format_script_text(d_sid, d_p)}", unsafe_allow_html=True)

                    c_d_edit.button("✏️", key=f"edit_de_{i}_{idx}", on_click=edit_dice_script, args=(i, idx),
                                    help="Редактировать")
                    c_d_del.button("❌", key=f"del_de_{i}_{idx}", on_click=delete_dice_script, args=(i, idx),
                                   help="Удалить")

                    if t not in final_dice_scripts_dict: final_dice_scripts_dict[t] = []
                    final_dice_scripts_dict[t].append(ds['data'])

                new_die = Dice(d_min, d_max, DiceType[dtype_str.upper()], is_counter=d_counter,
                               scripts=final_dice_scripts_dict)
                dice_objects.append(new_die)

    return dice_objects