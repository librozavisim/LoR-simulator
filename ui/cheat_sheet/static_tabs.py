import streamlit as st
import pandas as pd
from core.game_templates import CHARACTER_TEMPLATES


def render_speed_tab():
    st.header("Скорость и Кубики Скорости")
    st.markdown("*(При условии прокачки Ловкости и Скорости)*")

    data_speed = [
        {"Lvl": "90+", "Rank": "Несовершенство (Impurity)", "Dice Slots": "6x [30-40]", "Agility": "40 (+35)",
         "Speed": "40 (+30)"},
        {"Lvl": "80", "Rank": "Цвет (Звезда Усложнен)", "Dice Slots": "6x [24-27]", "Agility": "30 (+25)",
         "Speed": "30 (+20)"},
        {"Lvl": "65", "Rank": "Rank 1 (Звезда)", "Dice Slots": "5x [21-24], 1x [19-22]", "Agility": "25 (+20)",
         "Speed": "30 (+16)"},
        {"Lvl": "50", "Rank": "Rank 2 (Кошмар Усложнен)", "Dice Slots": "4x [19-22], 1x [14-17]", "Agility": "20 (+20)",
         "Speed": "25 (+16)"},
        {"Lvl": "43", "Rank": "Rank 3 (Кошмар)", "Dice Slots": "3x [16-19], 1x [13-16]", "Agility": "17 (+15)",
         "Speed": "22 (+12)"},
        {"Lvl": "36", "Rank": "Rank 4 (Чума Усложнен)", "Dice Slots": "3x [15-18], 1x [10-13]", "Agility": "14 (+15)",
         "Speed": "19 (+12)"},
        {"Lvl": "30", "Rank": "Rank 5 (Чума)", "Dice Slots": "2x [13-16], 1x [10-13]", "Agility": "12 (+10)",
         "Speed": "16 (+8)"},
        {"Lvl": "24", "Rank": "Rank 6 (Легенда Усложнен)", "Dice Slots": "2x [12-15], 1x [7-10]", "Agility": "10 (+10)",
         "Speed": "13 (+8)"},
        {"Lvl": "18", "Rank": "Rank 7 (Легенда)", "Dice Slots": "1x [10-13], 1x [7-10]", "Agility": "8 (+5)",
         "Speed": "10 (+4)"},
        {"Lvl": "12", "Rank": "Rank 8 (Миф)", "Dice Slots": "1x [9-12], 1x [4-7]", "Agility": "6 (+5)",
         "Speed": "7 (+4)"},
        {"Lvl": "6", "Rank": "Rank 9 (Слухи Усложнен)", "Dice Slots": "1x [4-7]", "Agility": "4 (+0)",
         "Speed": "4 (+0)"},
        {"Lvl": "0", "Rank": "Крысы (Слухи)", "Dice Slots": "1x [1-3]", "Agility": "1 (+0)", "Speed": "1 (+0)"},
    ]
    st.table(pd.DataFrame(data_speed))


def render_hp_tab():
    st.header("Расчет Здоровья (HP)")
    st.markdown("*(При условии прокачки Стойкости)*")

    hp_rows = []
    for tmpl in reversed(CHARACTER_TEMPLATES):
        hp_rows.append({
            "Lvl": str(tmpl['level']),
            "Rank": tmpl['rank_name'],
            "Endurance": tmpl['endurance'],
            "Total HP (Approx)": tmpl['hp_approx']
        })

    st.dataframe(pd.DataFrame(hp_rows), width=1000, hide_index=True)


def render_power_tab():
    st.header("Чистые средние роллы карты")
    st.caption("Детальная разбивка источников силы.")

    data_power = [
        {"Lvl": 80, "Rank": "Color", "Base Roll": "25-32", "Str": "+5", "W.Type": "+5", "Talents": "+2", "W.Rank": "+5",
         "Imp": "+10", "Total Avg": "56 (29+27)"},
        {"Lvl": 65, "Rank": "Rank 1", "Base Roll": "21-27", "Str": "+5", "W.Type": "+5", "Talents": "+2",
         "W.Rank": "+5", "Imp": "+9", "Total Avg": "50 (24+26)"},
        {"Lvl": 50, "Rank": "Rank 2", "Base Roll": "17-22", "Str": "+4", "W.Type": "+5", "Talents": "+2",
         "W.Rank": "+4", "Imp": "+8", "Total Avg": "42 (19+23)"},
        {"Lvl": 43, "Rank": "Rank 3", "Base Roll": "14-19", "Str": "+4", "W.Type": "+4", "Talents": "+2",
         "W.Rank": "+4", "Imp": "+7", "Total Avg": "38 (17+21)"},
        {"Lvl": 36, "Rank": "Rank 4", "Base Roll": "11-16", "Str": "+3", "W.Type": "+4", "Talents": "+2",
         "W.Rank": "+3", "Imp": "+6", "Total Avg": "31 (13+18)"},
        {"Lvl": 30, "Rank": "Rank 5", "Base Roll": "9-13", "Str": "+2", "W.Type": "+3", "Talents": "+2", "W.Rank": "+3",
         "Imp": "+5", "Total Avg": "26 (11+15)"},
        {"Lvl": 24, "Rank": "Rank 6", "Base Roll": "7-10", "Str": "+2", "W.Type": "+3", "Talents": "0", "W.Rank": "+3",
         "Imp": "+4", "Total Avg": "20 (8+12)"},
        {"Lvl": 18, "Rank": "Rank 7", "Base Roll": "5-7", "Str": "+2", "W.Type": "+2", "Talents": "0", "W.Rank": "+2",
         "Imp": "+3", "Total Avg": "15 (6+9)"},
        {"Lvl": 12, "Rank": "Rank 8", "Base Roll": "4-6", "Str": "+1", "W.Type": "+1", "Talents": "0", "W.Rank": "+1",
         "Imp": "+2", "Total Avg": "10 (5+5)"},
        {"Lvl": 6, "Rank": "Rank 9", "Base Roll": "3-5", "Str": "1/0", "W.Type": "1/0", "Talents": "0", "W.Rank": "0/1",
         "Imp": "+1", "Total Avg": "9 / 4"},
    ]
    st.table(pd.DataFrame(data_power))
    st.info(
        "**Легенда:** Str = Сила | W.Type = Тип оружия | Talents = Бонус веток | W.Rank = Ранг оружия | Imp = Импланты")


def render_eco_tab():
    st.header("💰 Экономика Города")
    with st.container(border=True):
        st.subheader("Доходы")
        st.metric("Средняя ЗП Перьев (в месяц)", "40,000,000 Ан", help="Чуть выше средней зарплаты в Гнезде")

    st.divider()
    st.subheader("📋 Прайс-лист на Ликвидацию")

    eco_data = [
        {"Цель": "10 Крыс", "Стоимость (Ан)": "10,000"},
        {"Цель": "Жилец Подворотен (< 9 ранга)", "Стоимость (Ан)": "10,000 - 100,000"},
        {"Цель": "Корректировщик 9 ранга", "Стоимость (Ан)": "100,000 - 500,000"},
        {"Цель": "Корректировщик 7-8 ранга", "Стоимость (Ан)": "500,000 - 3,000,000"},
        {"Цель": "Корректировщик 5-6 ранга", "Стоимость (Ан)": "3,000,000 - 10,000,000"},
        {"Цель": "Высокие ранги (Звезда / Цвет)", "Стоимость (Ан)": "100,000,000 - 1,000,000,000+"},
    ]
    st.table(pd.DataFrame(eco_data))


def render_mech_tab():
    st.header("💀 Особые Состояния")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("💔 Бессознательное состояние (HP < 0)")
            st.markdown("...")
    with c2:
        with st.container(border=True):
            st.subheader("🤯 Паника / Искажение (SP < 0)")
            st.markdown("...")