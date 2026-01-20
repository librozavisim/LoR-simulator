from logic.character_changing.passives.base_passive import BasePassive
from core.enums import DiceType
from core.logging import logger, LogLevel  # [NEW] Import
from logic.statuses.status_constants import NEGATIVE_STATUSES


# ==========================================
# 1.1 Держать себя в руках
# ==========================================
class TalentKeepItTogether(BasePassive):
    id = "keep_it_together"
    name = "Держать себя в руках"
    description = (
        "1.1 Ваш рассудок увеличивается на 20%.\n"
        "В панике (SP <= 0) вы получаете +(Макс. SP / 50) к силе бросков в бою."
    )
    is_active_ability = False

    def on_calculate_stats(self, unit) -> dict:
        return {"sp_pct": 20}

    def on_roll(self, ctx, **kwargs):
        stack = kwargs.get("stack", 0)
        if ctx.source.current_sp <= 0:
            bonus = ctx.source.max_sp // 50
            if bonus > 0:
                ctx.modify_power(bonus, "Panic (Keep It Together)")


# ==========================================
# 1.2 Центр у равновесия
# ==========================================
class TalentCenterOfBalance(BasePassive):
    id = "center_of_balance"
    name = "Центр у равновесия"
    description = (
        "1.2 В начале раунда восстанавливает 2 + (Max SP / 20) рассудка всем союзникам."
    )
    is_active_ability = False

    def on_round_start(self, unit, log_func, **kwargs):
        allies = kwargs.get("allies", [unit])  # По умолчанию только себя

        # Формула: 2 + (Макс СП / 20)
        bonus_from_max = unit.max_sp // 20
        heal_amount = 2 + bonus_from_max

        restored_count = 0
        for ally in allies:
            if ally.is_dead(): continue

            old_sp = ally.current_sp
            ally.current_sp = min(ally.max_sp, ally.current_sp + heal_amount)
            diff = ally.current_sp - old_sp

            if diff > 0: restored_count += 1

        # Логируем
        if log_func and restored_count > 0:
            log_func(f"🧠 {self.name}: Восстановлено {heal_amount} SP ({restored_count} союзникам).")

        if restored_count > 0:
            logger.log(f"🧠 Center of Balance: Healed {heal_amount} SP for {restored_count} allies", LogLevel.VERBOSE,
                       "Talent")


# ==========================================
# 1.3 Чай ("ты делаешь великолепный чай")
# ==========================================
class TalentTeaMaster(BasePassive):
    id = "tea_master"
    name = "Чай [WIP]"
    description = (
        "1.3 Вы получаете рецепт особых чаев.\n\n"
        "☕ **Особый тёмный чай**: Восстанавливает 15% SP (мин 10) и дает +3 Интеллекта на час.\n"
        "🍃 **Особый зелёный чай**: Восстанавливает 15% SP (мин 10) и дает 20% временных ХП на час.\n"
        "🍎 **Особый Фруктовый чай**: Восстанавливает 15% SP (мин 10) и дает 2 Спешки на час.\n"
        "🌸 **Чай из листьев сакуры**: Восстанавливает 100% SP. (Можно в бою, нужен бросок Ловкости).\n"
        "🍓 **Ягодный Чай**: Восстанавливает 15% SP и дает +1 Выдержку на час.\n"
        "🫚 **Имбирный чай**: Восстанавливает 15% SP. Даёт возможность избежать наложения отрицательного эффекта.\n"
        "🌺 **Красный чай**: Восстанавливает 15% SP. Дает +1 Силу на час.\n"
        "☕ **Кофе-чай**: Восстанавливает SP... имеет 1% шанс убить вас.\n"
    )
    active = True

    def on_combat_start(self, unit, log_func, **kwargs):
        tea_ids = [
            "tea_dark", "tea_green", "tea_fruit",
            "tea_sakura", "tea_berry", "tea_red", "tea_ginger", "tea_coffee"
        ]
        added_count = 0
        for tid in tea_ids:
            if tid not in unit.deck:
                unit.deck.append(tid)
                added_count += 1

        if log_func:
            log_func(f"☕ **Чайный Мастер**: {added_count} видов чая добавлено в инвентарь.")

        logger.log(f"☕ Tea Master: Added {added_count} tea cards to {unit.name}", LogLevel.NORMAL, "Talent")


# ==========================================
# 1.4 Ума помрачительная сила
# ==========================================
class TalentMindPower(BasePassive):
    id = "mind_power"
    name = "Умопомрачительная сила"
    description = (
        "1.4 Активно: Потратить SP (10-50), чтобы получить Силу (1-5) на этот раунд.\n"
        "Конвертация 10 к 1."
    )
    is_active_ability = True
    cooldown = 1

    conversion_options = {
        "10 SP -> +1 Strength": {"cost": 10, "amt": 1},
        "20 SP -> +2 Strength": {"cost": 20, "amt": 2},
        "30 SP -> +3 Strength": {"cost": 30, "amt": 3},
        "40 SP -> +4 Strength": {"cost": 40, "amt": 4},
        "50 SP -> +5 Strength": {"cost": 50, "amt": 5},
    }

    def activate(self, unit, log_func, choice_key=None, **kwargs):
        if unit.cooldowns.get(self.id, 0) > 0:
            return False

        if not choice_key or choice_key not in self.conversion_options:
            if log_func: log_func("⚠️ Выберите уровень усиления в списке.")
            return False

        data = self.conversion_options[choice_key]
        cost = data["cost"]
        amount = data["amt"]

        if unit.current_sp < cost:
            if log_func: log_func(f"❌ Недостаточно Рассудка! (Нужно {cost}, есть {unit.current_sp})")
            return False

        unit.current_sp -= cost
        unit.add_status("strength", amount, duration=1)

        if log_func:
            log_func(f"🧠 **{self.name}**: Пожертвовано {cost} SP -> Получено +{amount} Силы!")

        logger.log(f"🧠 Mind Power: {unit.name} spent {cost} SP for +{amount} Strength", LogLevel.NORMAL, "Talent")

        unit.cooldowns[self.id] = self.cooldown
        return True


# ==========================================
# 1.5 Пик рассудительности
# ==========================================
class TalentPeakSanity(BasePassive):
    id = "peak_sanity"
    name = "Пик рассудительности"
    description = (
        "1.5 Если SP > 50%: Мин. бросок +2.\n"
        "Ясность (Clarity): Тратится для отмены негативных эффектов.\n"
        "Макс = SP/50. Реген 1 заряд раз в 5 раундов."
    )
    is_active_ability = False

    def _get_max_clarity(self, unit):
        sp = getattr(unit, 'max_sp', 20)
        return max(1, sp // 50)

    def on_combat_start(self, unit, log_func, **kwargs):
        if unit.memory.get("peak_sanity_initialized"):
            return

        max_c = self._get_max_clarity(unit)
        unit.add_status("clarity", max_c, duration=99)
        unit.memory["clarity_cooldown_counter"] = 0
        unit.memory["peak_sanity_initialized"] = True

        if log_func:
            log_func(f"✨ **Ясность**: Получено {max_c} зарядов (Максимум).")

    def on_roll(self, ctx, **kwargs):
        stack = kwargs.get("stack", 0)
        if ctx.source.max_sp > 0:
            ratio = ctx.source.current_sp / ctx.source.max_sp
            if ratio > 0.5:
                limit = ctx.dice.min_val + 2
                if ctx.base_value < limit:
                    diff = limit - ctx.base_value
                    ctx.modify_power(diff, "Peak Sanity (Min+2)")

    def on_round_end(self, unit, log_func=None, **kwargs):
        limit = self._get_max_clarity(unit)
        current = unit.get_status("clarity")

        if current < limit:
            counter = unit.memory.get("clarity_cooldown_counter", 0) + 1

            if counter >= 5:
                unit.add_status("clarity", 1, duration=99)
                unit.memory["clarity_cooldown_counter"] = 0
                if log_func: log_func(f"✨ **Ясность**: Регенерация +1 (5 раундов прошло).")
                logger.log(f"✨ Clarity Regen: {unit.name} +1 charge", LogLevel.VERBOSE, "Talent")
            else:
                unit.memory["clarity_cooldown_counter"] = counter

    def on_before_status_add(self, unit, status_id, amount):

        if status_id in NEGATIVE_STATUSES:
            clarity = unit.get_status("clarity")
            if clarity > 0:
                unit.remove_status("clarity", 1)
                logger.log(f"✨ Clarity Block: {unit.name} blocked {status_id}", LogLevel.NORMAL, "Talent")
                return False, f"✨ Clarity blocked **{status_id}**! (-1 stack)"

        return True, None


# ==========================================
# 1.6 Психическая нагрузка
# ==========================================
class TalentPsychicStrain(BasePassive):
    id = "psychic_strain"
    name = "Психическая нагрузка"
    description = (
        "1.6 Каждая ваша атака дополнительно наносит 4% от вашего максимального рассудка белым уроном (SP damage)."
    )
    is_active_ability = False

    def on_hit(self, ctx, **kwargs):
        # 1. Проверяем, есть ли цель
        if not ctx.target: return

        # 2. Проверяем, что это Атакующий кубик
        if ctx.dice.dtype not in [DiceType.SLASH, DiceType.PIERCE, DiceType.BLUNT]:
            return

        # 3. Считаем 4% от Макс SP
        sp_dmg = int(ctx.source.max_sp * 0.04)

        if sp_dmg > 0:
            ctx.target.take_sanity_damage(sp_dmg)
            ctx.log.append(f"🧠 **{self.name}**: +{sp_dmg} SP Dmg (Белый урон)")
            logger.log(f"🧠 Psychic Strain: Dealt {sp_dmg} SP damage to {ctx.target.name}", LogLevel.VERBOSE, "Talent")


# ==========================================
# 1.7 Невыносимое присутствие
# ==========================================
class TalentUnbearablePresence(BasePassive):
    id = "unbearable_presence"
    name = "Невыносимое присутствие [WIP roll advantage]"
    description = (
        "1.7 Все враги, видящие вас, получают 2.5% от вашего Макс. SP уроном в начале раунда.\n"
        "(Не работает, если на вас статус Stealth/Невидимость)."
    )
    is_active_ability = False

    def on_round_start(self, unit, log_func, **kwargs):
        if unit.get_status("stealth") > 0 or unit.get_status("invisible") > 0:
            return

        enemies = kwargs.get("enemies")
        if not enemies:
            op = kwargs.get("opponent")
            enemies = [op] if op else []

        dmg = int(unit.max_sp * 0.025)
        if dmg < 1 and unit.max_sp > 0: dmg = 1
        if dmg <= 0: return

        hit_count = 0
        for enemy in enemies:
            if enemy and not enemy.is_dead():
                enemy.take_sanity_damage(dmg)
                hit_count += 1

        if log_func and hit_count > 0:
            log_func(f"👁️ **{self.name}**: {hit_count} врагов подавлены (-{dmg} SP)")

        if hit_count > 0:
            logger.log(f"👁️ Unbearable Presence: {hit_count} enemies took {dmg} SP damage", LogLevel.VERBOSE, "Talent")


# ==========================================
# 1.8 Эмоциональный шторм
# ==========================================
class TalentEmotionalStorm(BasePassive):
    id = "emotional_storm"
    name = "Эмоциональный шторм"
    description = (
        "1.8 Механика Эмоционального Уровня (0-5).\n"
        "Получайте Позитивные/Негативные эмоции за макс/мин броски и исходы столкновений."
    )
    is_active_ability = False

    def _get_threshold(self, level):
        thresholds = {0: 3, 1: 6, 2: 11, 3: 18, 4: 27}
        return thresholds.get(level, 999)

    def _gain_coin(self, unit, kind, ctx):
        if "emo_level" not in unit.memory: return
        lvl = unit.memory["emo_level"]
        if lvl >= 5: return

        unit.memory["emo_progress"] += 1
        if kind == "pos":
            unit.memory["emo_coins_pos"] += 1
            if ctx and hasattr(ctx, 'log') and ctx.log is not None:
                ctx.log.append("🟢 **Эмоции**: +1 Позитивная монета")
        else:
            unit.memory["emo_coins_neg"] += 1
            if ctx and hasattr(ctx, 'log') and ctx.log is not None:
                ctx.log.append("🔴 **Эмоции**: +1 Негативная монета")

    def on_round_start(self, unit, log_func, **kwargs):
        if not unit.memory.get("emotional_storm_initialized"):
            unit.memory["emotional_storm_initialized"] = True
            unit.memory["emo_level"] = 0
            unit.memory["emo_progress"] = 0
            unit.memory["emo_coins_pos"] = 0
            unit.memory["emo_coins_neg"] = 0
            if log_func: log_func(f"🌪️ **{self.name}**: Начало отсчета эмоций.")

        lvl = unit.memory.get("emo_level", 0)
        if lvl > 0:
            buffs = []
            if lvl >= 1:
                unit.add_status("haste", 2, duration=1)
                buffs.append("Haste")
            if lvl >= 2:
                unit.add_status("endurance", 2, duration=1)
                buffs.append("Endurance")
            if lvl >= 3:
                unit.add_status("protection", 2, duration=1)
                buffs.append("Protection")
            if lvl >= 4:
                unit.add_status("strength", 2, duration=1)
                buffs.append("Strength")
            if lvl >= 5:
                unit.add_status("haste", 2, duration=1)
                unit.add_status("strength", 2, duration=1)
                buffs.append("All+1")

            if log_func:
                log_func(f"🌪️ **Эмоции (Ур. {lvl})**: Баффы активированы ({', '.join(buffs)}).")

            logger.log(f"🌪️ Emotional Storm Lvl {lvl}: Applied buffs {buffs}", LogLevel.VERBOSE, "Talent")

    def on_roll(self, ctx, **kwargs):
        if not ctx.dice: return
        if ctx.base_value == ctx.dice.max_val:
            self._gain_coin(ctx.source, "pos", ctx)
        elif ctx.base_value == ctx.dice.min_val:
            self._gain_coin(ctx.source, "neg", ctx)

    def on_clash_win(self, ctx, **kwargs):
        self._gain_coin(ctx.source, "pos", ctx)

    def on_clash_lose(self, ctx, **kwargs):
        self._gain_coin(ctx.source, "neg", ctx)

    def on_round_end(self, unit, log_func, **kwargs):
        lvl = unit.memory.get("emo_level", 0)
        progress = unit.memory.get("emo_progress", 0)

        if lvl < 5:
            req = self._get_threshold(lvl)
            if progress >= req:
                unit.memory["emo_level"] += 1
                new_lvl = unit.memory["emo_level"]
                if log_func:
                    log_func(f"⚡ **Эмоциональный Уровень повышен!** ({new_lvl - 1} -> {new_lvl})")

                logger.log(f"⚡ Emotional Level Up: {unit.name} reached level {new_lvl}", LogLevel.NORMAL, "Talent")

                unit.current_sp = min(unit.max_sp, unit.current_sp + 10)

        if unit.memory.get("emo_level", 0) >= 5:
            unit.active_buffs["berserker_rage"] = 2
            if log_func:
                log_func("😡 **Эмоции (MAX)**: Получен доп. слот на след. раунд!")

        pos = unit.memory.get("emo_coins_pos", 0)
        neg = unit.memory.get("emo_coins_neg", 0)

        if log_func:
            log_func(f"🌪️ **Эмоции (Итог)**: 🟢 {pos} | 🔴 {neg}")

        if pos == 0 and neg == 0: return

        if pos > neg:
            heal_sp = (pos - neg) * 2
            unit.current_sp = min(unit.max_sp, unit.current_sp + heal_sp)
            if log_func: log_func(f" **Позитив**: Восстановлено {heal_sp} SP.")
        elif neg > pos:
            heal_hp = (neg - pos) * 2
            unit.heal_hp(heal_hp)
            if log_func: log_func(f" **Негатив**: Восстановлено {heal_hp} HP.")


# ==========================================
# 1.9 А: Безопасное ЭГО
# ==========================================
class TalentSafeEGO(BasePassive):
    id = "safe_ego"
    name = "Безопасное ЭГО (А) [WIP]"
    description = (
        "1.9 А: Если вы начнете ломаться психически, вы гарантированно получите ЭГО и не будете иметь риск стать Искажением."
    )
    is_active_ability = False


# ==========================================
# 1.9 Б: Не теряя себя
# ==========================================
class TalentControlledDistortion(BasePassive):
    id = "controlled_distortion"
    name = "Не теряя себя (Б) [WIP]"
    description = (
        "1.9 Б: Если вы начнете ломаться психически, вы станете Искажением, но не потеряете рассудок.\n"
        "Пассивное умение и макс. порог характеристик многократно усиливаются."
    )
    is_active_ability = False