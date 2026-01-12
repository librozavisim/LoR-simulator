# ui/cheat_sheet.py
import streamlit as st
import pandas as pd


def render_cheat_sheet_page():
    st.title("📚 Справочник характеристик")
    st.caption("Референсные значения и экономика Города.")

    tab_speed, tab_hp, tab_power, tab_eco, tab_mech, tab_balance = st.tabs([
        "💨 Скорость", "❤️ Здоровье", "⚔️ Сила", "💰 Экономика", "💀 Механики", "⚖️ Конструктор"
    ])
    base_rolls_data = [
        (0, "Крысы", 1, 3),
        (6, "Слухи (Rank 9)", 3, 5),
        (12, "Миф (Rank 8)", 4, 6),
        (18, "Легенда (Rank 7)", 5, 7),
        (24, "Легенда+ (Rank 6)", 7, 10),
        (30, "Чума (Rank 5)", 9, 13),
        (36, "Чума+ (Rank 4)", 11, 16),
        (43, "Кошмар (Rank 3)", 14, 19),
        (50, "Кошмар+ (Rank 2)", 17, 22),
        (65, "Звезда (Rank 1)", 21, 27),
        (80, "Цвет (Color)", 25, 32),
        (90, "Несовершенство", 30, 40),
    ]
    # === ТАБ 1: СКОРОСТЬ ===
    with tab_speed:
        st.header("Скорость и Кубики Скорости")
        st.markdown("*(При условии прокачки Ловкости и Скорости)*")

        data_speed = [
            {"Lvl": "90+", "Rank": "Несовершенство (Impurity)", "Dice Slots": "6x [30-40]", "Agility": "40 (+35)",
             "Speed": "40 (+30)"},
            {"Lvl": 80, "Rank": "Цвет (Звезда Усложнен)", "Dice Slots": "6x [24-27]", "Agility": "30 (+25)",
             "Speed": "30 (+20)"},
            {"Lvl": 65, "Rank": "Rank 1 (Звезда)", "Dice Slots": "5x [21-24], 1x [19-22]", "Agility": "25 (+20)",
             "Speed": "30 (+16)"},
            {"Lvl": 50, "Rank": "Rank 2 (Кошмар Усложнен)", "Dice Slots": "4x [19-22], 1x [14-17]",
             "Agility": "20 (+20)", "Speed": "25 (+16)"},
            {"Lvl": 43, "Rank": "Rank 3 (Кошмар)", "Dice Slots": "3x [16-19], 1x [13-16]", "Agility": "17 (+15)",
             "Speed": "22 (+12)"},
            {"Lvl": 36, "Rank": "Rank 4 (Чума Усложнен)", "Dice Slots": "3x [15-18], 1x [10-13]", "Agility": "14 (+15)",
             "Speed": "19 (+12)"},
            {"Lvl": 30, "Rank": "Rank 5 (Чума)", "Dice Slots": "2x [13-16], 1x [10-13]", "Agility": "12 (+10)",
             "Speed": "16 (+8)"},
            {"Lvl": 24, "Rank": "Rank 6 (Легенда Усложнен)", "Dice Slots": "2x [12-15], 1x [7-10]",
             "Agility": "10 (+10)", "Speed": "13 (+8)"},
            {"Lvl": 18, "Rank": "Rank 7 (Легенда)", "Dice Slots": "1x [10-13], 1x [7-10]", "Agility": "8 (+5)",
             "Speed": "10 (+4)"},
            {"Lvl": 12, "Rank": "Rank 8 (Миф)", "Dice Slots": "1x [9-12], 1x [4-7]", "Agility": "6 (+5)",
             "Speed": "7 (+4)"},
            {"Lvl": 6, "Rank": "Rank 9 (Слухи Усложнен)", "Dice Slots": "1x [4-7]", "Agility": "4 (+0)",
             "Speed": "4 (+0)"},
            {"Lvl": 0, "Rank": "Крысы (Слухи)", "Dice Slots": "1x [1-3]", "Agility": "1 (+0)", "Speed": "1 (+0)"},
        ]
        df_speed = pd.DataFrame(data_speed)
        st.table(df_speed)

    # === ТАБ 2: ЗДОРОВЬЕ ===
    with tab_hp:
        st.header("Расчет Здоровья (HP)")
        st.markdown("*(При условии прокачки Стойкости)*")

        data_hp = [
            {"Lvl": "90+", "Rank": "Несовершенство", "Endurance": 100, "Total HP": "~950-1200"},
            {"Lvl": 80, "Rank": "Цвет (Звезда+)", "Endurance": 90, "Total HP": 726},
            {"Lvl": 65, "Rank": "Rank 1 (Звезда)", "Endurance": 80, "Total HP": 525},
            {"Lvl": 50, "Rank": "Rank 2 (Кошмар+)", "Endurance": 70, "Total HP": 351},
            {"Lvl": 43, "Rank": "Rank 3 (Кошмар)", "Endurance": 60, "Total HP": 293},
            {"Lvl": 36, "Rank": "Rank 4 (Чума+)", "Endurance": 50, "Total HP": 239},
            {"Lvl": 30, "Rank": "Rank 5 (Чума)", "Endurance": 40, "Total HP": 189},
            {"Lvl": 24, "Rank": "Rank 6 (Легенда+)", "Endurance": 30, "Total HP": 145},
            {"Lvl": 18, "Rank": "Rank 7 (Легенда)", "Endurance": 20, "Total HP": 104},
            {"Lvl": 12, "Rank": "Rank 8 (Миф)", "Endurance": 10, "Total HP": 68},
            {"Lvl": 6, "Rank": "Rank 9 (Слухи+)", "Endurance": 5, "Total HP": 42},
            {"Lvl": 0, "Rank": "Крысы", "Endurance": 0, "Total HP": 20},
        ]
        df_hp = pd.DataFrame(data_hp)
        st.dataframe(df_hp, use_container_width=True, hide_index=True)

    # === ТАБ 3: РОЛЛЫ ===
    with tab_power:
        st.header("Чистые средние роллы карты")
        st.caption("Детальная разбивка источников силы.")

        # Расширенная таблица с колонками для каждого бонуса
        data_power = [
            {
                "Lvl": 80, "Rank": "Color", "Base Roll": "25-32",
                "Str": "+5", "W.Type": "+5", "Talents": "+2", "W.Rank": "+5", "Imp": "+10",
                "Total Avg": "56 (29+27)"
            },
            {
                "Lvl": 65, "Rank": "Rank 1", "Base Roll": "21-27",
                "Str": "+5", "W.Type": "+5", "Talents": "+2", "W.Rank": "+5", "Imp": "+9",
                "Total Avg": "50 (24+26)"
            },
            {
                "Lvl": 50, "Rank": "Rank 2", "Base Roll": "17-22",
                "Str": "+4", "W.Type": "+5", "Talents": "+2", "W.Rank": "+4", "Imp": "+8",
                "Total Avg": "42 (19+23)"
            },
            {
                "Lvl": 43, "Rank": "Rank 3", "Base Roll": "14-19",
                "Str": "+4", "W.Type": "+4", "Talents": "+2", "W.Rank": "+4", "Imp": "+7",
                "Total Avg": "38 (17+21)"
            },
            {
                "Lvl": 36, "Rank": "Rank 4", "Base Roll": "11-16",
                "Str": "+3", "W.Type": "+4", "Talents": "+2", "W.Rank": "+3", "Imp": "+6",
                "Total Avg": "31 (13+18)"
            },
            {
                "Lvl": 30, "Rank": "Rank 5", "Base Roll": "9-13",
                "Str": "+2", "W.Type": "+3", "Talents": "+2", "W.Rank": "+3", "Imp": "+5",
                "Total Avg": "26 (11+15)"
            },
            {
                "Lvl": 24, "Rank": "Rank 6", "Base Roll": "7-10",
                "Str": "+2", "W.Type": "+3", "Talents": "0", "W.Rank": "+3", "Imp": "+4",
                "Total Avg": "20 (8+12)"
            },
            {
                "Lvl": 18, "Rank": "Rank 7", "Base Roll": "5-7",
                "Str": "+2", "W.Type": "+2", "Talents": "0", "W.Rank": "+2", "Imp": "+3",
                "Total Avg": "15 (6+9)"
            },
            {
                "Lvl": 12, "Rank": "Rank 8", "Base Roll": "4-6",
                "Str": "+1", "W.Type": "+1", "Talents": "0", "W.Rank": "+1", "Imp": "+2",
                "Total Avg": "10 (5+5)"
            },
            {
                "Lvl": 6, "Rank": "Rank 9", "Base Roll": "3-5",
                "Str": "1/0", "W.Type": "1/0", "Talents": "0", "W.Rank": "0/1", "Imp": "+1",
                "Total Avg": "9 / 4"
            },
        ]

        df_power = pd.DataFrame(data_power)
        # Настройка отображения колонок
        st.table(df_power)

        st.info(
            "**Легенда:** Str = Сила | W.Type = Тип оружия | Talents = Бонус веток | W.Rank = Ранг оружия | Imp = Импланты")

    # === ТАБ 4: ЭКОНОМИКА ===
    with tab_eco:
        st.header("💰 Экономика Города")

        with st.container(border=True):
            st.subheader("Доходы")
            st.metric("Средняя ЗП Перьев (в месяц)", "40,000,000 Ан", help="Чуть выше средней зарплаты в Гнезде")

        st.divider()

        st.subheader("📋 Прайс-лист на Ликвидацию (Ориентировочно)")
        st.caption("Цены для легальных контрактов. Нелегальные заказы стоят дороже. Цены зависят от сложности и целей.")

        eco_data = [
            {"Цель": "10 Крыс", "Стоимость (Ан)": "10,000"},
            {"Цель": "Жилец Подворотен / Преступник (< 9 ранга)", "Стоимость (Ан)": "10,000 - 100,000"},
            {"Цель": "Корректировщик 9 ранга", "Стоимость (Ан)": "100,000 - 500,000"},
            {"Цель": "Корректировщик 7-8 ранга", "Стоимость (Ан)": "500,000 - 3,000,000"},
            {"Цель": "Корректировщик 5-6 ранга", "Стоимость (Ан)": "3,000,000 - 10,000,000"},
            {"Цель": "Высокие ранги (Звезда / Цвет)", "Стоимость (Ан)": "100,000,000 - 1,000,000,000+"},
        ]

        df_eco = pd.DataFrame(eco_data)
        st.table(df_eco)

        st.info(
            "💡 Примечание: Для рангов выше 5-го (Городская Чума) цена растет экспоненциально (примерно х10 за ранг), но больше зависит от конкретных условий и целей, чем от фиксированного прайса.")
    # === ТАБ 5: МЕХАНИКИ ===
    with tab_mech:
        st.header("💀 Особые Состояния")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.subheader("💔 Бессознательное состояние (HP < 0)")
                st.markdown("...")  # (Текст механики, который мы добавляли ранее)
        with c2:
            with st.container(border=True):
                st.subheader("🤯 Паника / Искажение (SP < 0)")
                st.markdown("...")  # (Текст механики)
        # === ТАБ 6: БАЛАНС (КОНСТРУКТОР) ===
    with tab_balance:
        st.header("⚖️ Конструктор Баланса Карт")
        st.caption("Калькулятор значений на основе ваших базовых роллов.")

        # --- 1. Таблица базовых бюджетов ---
        with st.expander("📊 Таблица Бюджетов (Power Budget)", expanded=True):
            budget_rows = []
            for _, rank_name, b_min, b_max in base_rolls_data:
                avg = (b_min + b_max) / 2
                budget_rows.append({
                    "Rank": rank_name,
                    "Base Roll": f"{b_min}-{b_max}",
                    "Avg (1 Die)": f"{avg:.1f}",
                    "Budget 2d": f"{avg * 2:.1f}",
                    "Budget 3d": f"{avg * 3:.1f}",
                    "Budget 4d": f"{avg * 4:.1f}",
                    "Budget 5d": f"{avg * 5:.1f}",
                })

            st.table(pd.DataFrame(budget_rows))
            st.caption("*Budget = (Base Avg) × (Dice Count).*")

        st.divider()

        # --- 2. Калькулятор ---
        c_set, c_res = st.columns([1, 1])

        with c_set:
            st.subheader("🛠️ Настройка")

            # 1. Выбор персонажа (Базовая сила)
            base_avg = 2.0  # Fallback
            char_level_display = 0

            if 'roster' in st.session_state and st.session_state['roster']:
                roster_names = list(st.session_state['roster'].keys())
                sel_char = st.selectbox("Персонаж", roster_names, key="bal_char_sel")

                unit = st.session_state['roster'][sel_char]
                char_level_display = unit.level

                # Поиск в справочнике
                found_stat = base_rolls_data[0]
                for row in base_rolls_data:
                    if char_level_display >= row[0]:
                        found_stat = row
                    else:
                        break

                b_min, b_max = found_stat[2], found_stat[3]
                base_avg = (b_min + b_max) / 2

                st.caption(f"Lvl {char_level_display} ({found_stat[1]}) -> Base: {b_min}-{b_max} (Avg {base_avg})")
            else:
                st.warning("Создайте персонажа для расчета!")

            # 2. Ранг Карты (Определяет "Стандартное кол-во дайсов")
            # Rank 1 = 1 die budget, Rank 5 = 5 dice budget
            card_rank = st.selectbox("Ранг карты (Tier)", [1, 2, 3, 4, 5], index=0, key="bal_card_rank")
            standard_dice_capacity = card_rank

            # 3. Тип и Дайсы
            type_opts = {
                "Melee (100%)": 1.0,
                "Offensive (115%)": 1.15,
                "Ranged (125%)": 1.25,
                "Mass Attack (140%)": 1.40
            }
            ctype_label = st.selectbox("Тип карты", list(type_opts.keys()), index=0, key="bal_type")
            type_mult = type_opts[ctype_label]

            dice_count = st.slider("Количество дайсов", 1, 5, 2, key="bal_count")

            st.markdown("**Модификаторы:**")
            effects_count = st.number_input("Кол-во эффектов (-15%)", 0, 5, 0)
            cond_hard = st.number_input("Сложные условия (+20%)", 0, 3, 0)
            cond_easy = st.number_input("Легкие условия (-10%)", 0, 3, 0)

            variance = st.slider("Разброс (Variance)", 0, 20, 4)

        with c_res:
            st.subheader("🎯 Результат")

            # 1. Расчет Бюджета Карты
            # Budget = (Base Avg) * (Rank Capacity) * TypeMult
            # Пример: Rank 3 Melee -> Budget = Base * 3 * 1.0
            total_budget = base_avg * standard_dice_capacity * type_mult

            # 2. Модификаторы эффективности
            eff_pen = effects_count * 0.15
            cond_mod = (cond_hard * 0.20) - (cond_easy * 0.10)
            power_mod = 1.0 - eff_pen + cond_mod

            # Бюджет с учетом модов
            effective_budget = total_budget * power_mod

            # 3. Деление на дайсы + Правило "Концентрации"
            # Если берем меньше дайсов, чем положено рангу -> Бонус 20%
            avg_per_die = effective_budget / dice_count

            split_bonus_applied = False
            if dice_count < standard_dice_capacity:
                avg_per_die *= 1.2
                split_bonus_applied = True

            # 4. Variance Adjustment (+2% силы за единицу разброса > 4)
            var_factor = 1.0 + ((variance - 4) * 0.02)
            final_avg_die = avg_per_die * var_factor

            # 5. Min/Max
            d_min = int(final_avg_die - (variance / 2))
            d_max = int(final_avg_die + (variance / 2))

            if d_min < 1: d_min = 1; d_max = 1 + variance

            with st.container(border=True):
                st.metric("Среднее (1 кубик)", f"{final_avg_die:.1f}")
                st.markdown(f"### 🎲 {d_min} ~ {d_max}")

                bonus_text = " (+20% Bonus)" if split_bonus_applied else ""
                st.caption(f"Rank Cap: {standard_dice_capacity} dice | Split: {dice_count}{bonus_text}")

            st.info(f"""
                    **Логика:**
                    * **Base**: {base_avg} (Lvl {char_level_display})
                    * **Rank Budget**: x{standard_dice_capacity} (Tier {card_rank})
                    * **Split**: /{dice_count} {'(+20% Boost)' if split_bonus_applied else ''}
                    * **Mods**: {int(power_mod * 100)}%
                """)