from logic.character_changing.passives.base_passive import BasePassive

# ======================================================================================
# КОРЕНЬ (ROOT)
# ======================================================================================

class TalentScanner(BasePassive):
    id = "scanner"
    name = "2.0 Сканер"
    description = (
        "Пассивно: Вы всегда видите точные значения HP, SP, Stagger и Сопротивления всех врагов.\n"
        "Вы видите стрелки агрессии (кто кого бьет) до выбора карт."
    )
    is_active_ability = False


# ======================================================================================
# ВЕТКА А: "ИДЕАЛ" (The Paragon) — Подготовка и Тело
# ======================================================================================

class TalentDeepPockets(BasePassive):
    id = "deep_pockets"
    name = "2.1.A Походный Рюкзак"
    description = (
        "Ваш лимит колоды увеличивается на +1 карту каждого ранга.\n"
        "Вы можете менять колоду в любой момент вне боя."
    )
    is_active_ability = False

    def on_calculate_stats(self, unit) -> dict:
        return {"deck_size_bonus": 3}


class TalentLogistics(BasePassive):
    id = "logistics"
    name = "2.2.A Эффективная Логистика"
    description = (
        "Лимит колоды увеличивается ещё на +1 за каждые 10 очков Интеллекта.\n"
        "Пассивно: в первом ходу КД всех карт снижается на 1"
    )
    is_active_ability = False


class TalentAceOfAllTrades(BasePassive):
    id = "ace_of_all_trades"
    name = "2.3.A Туз всех мастей"
    description = (
        "Вы получаете бонус к МИНИМАЛЬНОМУ значению всех кубиков.\n"
        "Бонус равен: (Сумма всех ваших атрибутов / 40).\n"
        "Пример: Сумма статов 120 -> +3 к мин. роллу (1~10 станет 4~10)."
    )
    is_active_ability = False


class TalentSynergy(BasePassive):
    id = "skill_synergy"
    name = "2.4.A Синергия Навыков"
    description = (
        "За каждые 2 навыка уровня 'Мастер' (10+), вы получаете +4 HP и +4 SP.\n"
        "Ваше мастерство закаляет дух и тело."
    )
    is_active_ability = False


class TalentTireless(BasePassive):
    id = "tireless_paragon"
    name = "2.5.A Неутомимый"
    description = (
        "Завершение любой боевой сцены полностью восстанавливает Stagger (Выдержку).\n"
        "Иммунитет к эффектам 'Обездвиживание' (Bind) и 'Медлительность'."
    )
    is_active_ability = False


class TalentMomentum(BasePassive):
    id = "momentum"
    name = "2.6.A На Волне"
    description = (
        "Если в прошлом раунде вы выиграли все столкновения (Clash Win),\n"
        "в этом раунде вы получаете +1 Мощи (Power) и +1 Скорости (Haste)."
    )
    is_active_ability = False


class TalentLimitBreaker(BasePassive):
    id = "limit_breaker"
    name = "2.7.A Предел Совершенства"
    description = (
        "Максимальный лимит (кап) прокачки атрибутов повышается на +10.\n"
        "Ваши тренировки выходят за грань человеческих возможностей."
    )
    is_active_ability = False


class TalentPlotArmor(BasePassive):
    id = "plot_armor"
    name = "2.8.A Сюжетная Броня"
    description = (
        "1 раз за вылазку: При получении летального урона вы остаетесь с 1 HP,\n"
        "получаете 'Неуязвимость' до конца раунда и полностью восстанавливаете Stagger."
    )
    is_active_ability = False


class TalentUniversalSoldier(BasePassive):
    id = "universal_soldier"
    name = "2.9.A Универсальный Солдат"
    description = (
        "Пассивно: Если сумма ваших атрибутов > 120 (уровень ~10-12), вы получаете +1 Слот Действия в начале боя (на 3 хода).\n"
        "Если сумма > 180 (уровень ~20), Слот Действия дается навсегда."
    )
    is_active_ability = False


class TalentDominant(BasePassive):
    id = "dominant"
    name = "2.10.A Доминант (Финал А)"
    description = (
        "Если ваша сумма статов выше суммы статов врага:\n"
        "Вы наносите +25% Урона и получаете -25% Урона от него.\n"
        "Ваши атаки нельзя перехватить (Unopposed), если вы бьете первым."
    )
    is_active_ability = False


# ======================================================================================
# ВЕТКА Б: "КУКЛОВОД" (The Puppeteer) — Разум и Манипуляция
# ======================================================================================

class TalentViciousMockery(BasePassive):
    id = "vicious_mockery"
    name = "2.1.B Злой Язык"
    description = (
        "Красноречие считается боевым атрибутом.\n"
        "Любая ваша атака наносит дополнительный урон по Рассудку (SP),\n"
        "равный (Красноречие / 5)."
    )
    is_active_ability = False


class TalentVerbalBarrier(BasePassive):
    id = "verbal_barrier"
    name = "2.2.B Словесный Барьер"
    description = (
        "При использовании Защиты (Block/Evade) вы получаете бонус +1 к кубику\n"
        "за каждые 15 очков Красноречия."
    )
    is_active_ability = False


class TalentTacticalAnalysis(BasePassive):
    id = "tactical_analysis"
    name = "2.3.B Тактический Анализ (Ур. 2)"
    description = (
        "Расширение модуля Сканера.\n"
        "Пассивно: Вы видите ПАССИВНЫЕ способности врага и их описания.\n"
        "Вы видите диапазон Скорости (Speed Dice) и состав колоды врага (какие карты у него есть)."
    )
    is_active_ability = False


class TalentKnowYourEnemy(BasePassive):
    id = "know_your_enemy"
    name = "2.4.B Познай Врага"
    description = (
        "Если вы атакуете врага, чьи статы вам известны (через Сканер),\n"
        "вы получаете +1 Clash Power.\n"
        "Бонус растет на +1 каждый раунд боя с этим врагом (макс +5)."
    )
    is_active_ability = False


class TalentCardShuffler(BasePassive):
    id = "card_shuffler"
    name = "2.5.B Карточный Шулер"
    description = (
        "Активно (1 раз за бой): Выберите 2 карты в вашем сбросе.\n"
        "Они мгновенно возвращаются в руку, их стоимость становится 0 на этот ход."
    )
    is_active_ability = True


class TalentPredictiveAlgo(BasePassive):
    id = "predictive_algo"
    name = "2.6.B Предиктивные Алгоритмы (Ур. 3)"
    description = (
        "Финальное улучшение аналитического модуля.\n"
        "В начале раунда вы видите СТРЕЛКИ намерений (кто кого бьет) и\n"
        "конкретные КАРТЫ, которые враг положил в слоты, до фазы битвы."
    )
    is_active_ability = False


class TalentExposeWeakness(BasePassive):
    id = "expose_weakness"
    name = "2.7.B Вскрытие Защиты"
    description = (
        "Активно (Free Action): Укажите на врага. Следующая атака союзника по нему\n"
        "будет считать сопротивление цели как 'Fatal' (x2.0 урон).\n"
        "Кулдаун: 3 хода."
    )
    is_active_ability = True


class TalentPokerFace(BasePassive):
    id = "poker_face_rework"
    name = "2.8.B Хладнокровие"
    description = (
        "Вы иммунны к Панике.\n"
        "Если ваше SP падает ниже 30%, вы получаете +3 Power (Clash),\n"
        "так как ваши действия становятся абсолютно нечитаемыми."
    )
    is_active_ability = False


class TalentMerchantOfDeath(BasePassive):
    id = "merchant_of_death"
    name = "2.9.B Торговец Смертью"
    description = (
        "Активно: Потратить Кредиты (Уровень врага * 50), чтобы подкупить его.\n"
        "Обычный враг покидает бой. Элитный враг получает Stagger на 1 ход.\n"
        "Не работает на Боссов и Монстров (Искажения)."
    )
    is_active_ability = True


class TalentPuppetMaster(BasePassive):
    id = "puppet_master"
    name = "2.10.B Кукловод (Финал Б)"
    description = (
        "Пассивно: 1 раз за раунд, когда враг атакует кого-то,\n"
        "вы можете перенаправить эту атаку на любую другую цель (кроме самого атакующего).\n"
        "Вы управляете хаосом битвы."
    )
    is_active_ability = False


# ======================================================================================
# ОПЦИОНАЛЬНЫЕ ТАЛАНТЫ (OPTIONAL)
# Можно брать в дополнение к любой ветке при выполнении условий
# ======================================================================================

class TalentImprovisation(BasePassive):
    id = "opt_improvisation"
    name = "Импровизация (Опц.)"
    description = (
        "Требование: Интеллект 30+.\n"
        "Если у вас в руке нет карт Атаки, вы создаете временную карту 'Импровизированный удар'\n"
        "(Cost 0, 4-8 Blunt, On Hit: Draw 1)."
    )
    is_active_ability = False


class TalentSocialEngineer(BasePassive):
    id = "opt_social_eng"
    name = "Социальная Инженерия (Опц.)"
    description = (
        "Требование: Красноречие 40+.\n"
        "В начале боя вы можете выбрать одного врага. Он не будет атаковать вас 2 раунда,\n"
        "пока вы не атакуете его. (Не работает на Искажения)."
    )
    is_active_ability = False


class TalentHoarder(BasePassive):
    id = "opt_hoarder"
    name = "Барахольщик (Опц.)"
    description = (
        "Требование: Нет.\n"
        "Вы получаете специальный слот 'Карман'. В него можно положить 1 расходник (Граната/Хилка),\n"
        "который применяется мгновенно (Free Action) и не тратит слот действия."
    )
    is_active_ability = False


# ======================================================================================
# УЛЬТИМЕЙТ
# ======================================================================================

class TalentForesight(BasePassive):
    id = "foresight"
    name = "2.11 Я это предвидел"
    description = (
        "Ультимативная способность (1 раз за бой).\n"
        "Активно: Нажмите ПОСЛЕ бросков кубиков (но до урона).\n"
        "Время отматывается в начало раунда. Вы сохраняете память о бросках врага,\n"
        "а враг обязан перебросить кубики с помехой (Disadvantage, выбирается худший)."
    )
    is_active_ability = True