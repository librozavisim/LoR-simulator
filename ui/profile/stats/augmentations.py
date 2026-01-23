import streamlit as st


def render_augmentations(unit, u_key):
    """Отрисовка панели ручных модификаторов (аугментаций)."""
    with st.expander("💉 Аугментации и Модификаторы (Ручные)", expanded=False):
        c_aug1, c_aug2, c_aug3 = st.columns(3)

        with c_aug1:
            st.caption("HP Modifiers")
            new_hp_flat = st.number_input("HP Flat (+)", -999, 999, unit.implants_hp_flat, key=f"imp_hp_f_{u_key}")
            new_hp_pct = st.number_input("HP Pct (%)", -100, 500, unit.implants_hp_pct, key=f"imp_hp_p_{u_key}")

            if new_hp_flat != unit.implants_hp_flat or new_hp_pct != unit.implants_hp_pct:
                unit.implants_hp_flat = new_hp_flat
                unit.implants_hp_pct = new_hp_pct
                unit.recalculate_stats()
                st.rerun()

        with c_aug2:
            st.caption("SP Modifiers")
            new_sp_flat = st.number_input("SP Flat (+)", -999, 999, unit.implants_sp_flat, key=f"imp_sp_f_{u_key}")
            new_sp_pct = st.number_input("SP Pct (%)", -100, 500, unit.implants_sp_pct, key=f"imp_sp_p_{u_key}")

            if new_sp_flat != unit.implants_sp_flat or new_sp_pct != unit.implants_sp_pct:
                unit.implants_sp_flat = new_sp_flat
                unit.implants_sp_pct = new_sp_pct
                unit.recalculate_stats()
                st.rerun()

        with c_aug3:
            st.caption("Stagger Modifiers")
            new_stg_flat = st.number_input("Stg Flat (+)", -999, 999, unit.implants_stagger_flat,
                                           key=f"imp_stg_f_{u_key}")
            new_stg_pct = st.number_input("Stg Pct (%)", -100, 500, unit.implants_stagger_pct, key=f"imp_stg_p_{u_key}")

            if new_stg_flat != unit.implants_stagger_flat or new_stg_pct != unit.implants_stagger_pct:
                unit.implants_stagger_flat = new_stg_flat
                unit.implants_stagger_pct = new_stg_pct
                unit.recalculate_stats()
                st.rerun()