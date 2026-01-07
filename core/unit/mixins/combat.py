import random
from core.enums import DiceType
from core.card import Card
from core.dice import Dice


class UnitCombatMixin:
    """
    Боевая логика: броски инициативы, проверки состояния, кулдауны.
    """

    def roll_speed_dice(self):
        """Генерация активных слотов на раунд."""
        self.active_slots = []

        if self.is_dead():
            return

        # 1. Основные кубики (расчитанные из статов)
        for (d_min, d_max) in self.computed_speed_dice:
            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")
            val = max(1, random.randint(d_min, d_max) + mod)
            self.active_slots.append({
                'speed': val, 'card': None, 'target_slot': None, 'is_aggro': False
            })

        # 2. [GENERIC] Бонусные кубики от Талантов и Пассивок
        # (Заменяет хардкоды Frenzy, Berserker Rage и т.д.)
        extra_dice_count = 0

        # Импорт внутри метода во избежание циклов
        from logic.character_changing.talents import TALENT_REGISTRY
        from logic.character_changing.passives import PASSIVE_REGISTRY

        # Проверка Талантов
        for tid in self.talents:
            if tid in TALENT_REGISTRY:
                obj = TALENT_REGISTRY[tid]
                if hasattr(obj, "get_speed_dice_bonus"):
                    extra_dice_count += obj.get_speed_dice_bonus(self)

        # Проверка Пассивок
        for pid in self.passives:
            if pid in PASSIVE_REGISTRY:
                obj = PASSIVE_REGISTRY[pid]
                if hasattr(obj, "get_speed_dice_bonus"):
                    extra_dice_count += obj.get_speed_dice_bonus(self)

        # Генерация слотов для бонусных кубиков
        if extra_dice_count > 0:
            # Используем лучший диапазон скорости (как в ярости)
            if self.computed_speed_dice:
                d_min, d_max = self.computed_speed_dice[0]
            else:
                d_min, d_max = self.base_speed_min, self.base_speed_max

            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")

            for _ in range(extra_dice_count):
                val = max(1, random.randint(d_min, d_max) + mod)
                self.active_slots.append({
                    'speed': val, 'card': None, 'target_slot': None, 'is_aggro': False,
                    'source_effect': 'Talent 🌟'
                })

        # 3. СТАТУС: Red Lycoris (Спец. эффект слотов)
        if self.get_status("red_lycoris") > 0:
            for slot in self.active_slots:
                slot['prevent_redirection'] = True
                if not slot.get('source_effect'):
                    slot['source_effect'] = "Lycoris 🩸"

        # 4. ТАЛАНТ: МАХНУТЬ ХВОСТИКОМ (Специфичный слот с картой)
        if "wag_tail" in self.passives:
            if self.computed_speed_dice:
                d_min, d_max = self.computed_speed_dice[0]
            else:
                d_min, d_max = self.base_speed_min, self.base_speed_max

            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")
            val_tail = max(1, random.randint(d_min, d_max) + mod)

            card_tail = Card(
                id="tail_swipe_counter", name="Tail Counter",
                description="Counter Evade: Отражает атаку и сгорает.",
                dice_list=[Dice(5, 7, DiceType.EVADE, is_counter=True)]
            )

            self.active_slots.append({
                'speed': val_tail, 'card': card_tail, 'target_slot': -1, 'is_aggro': False,
                'source_effect': 'Tail Swipe 🐈', 'locked': True, 'consumed': False
            })

        # 5. ТАЛАНТ: ОБОРОНА (ZAFU)
        if "defense_zafu" in self.talents:
            zafu_dice_list = []
            zafu_dice_list.append(Dice(5, 7, DiceType.BLOCK, is_counter=False))

            if "talent_3_5" in self.talents:
                zafu_dice_list.append(Dice(5, 7, DiceType.BLOCK, is_counter=False))
            if "talent_3_8" in self.talents:
                zafu_dice_list.append(Dice(5, 7, DiceType.BLOCK, is_counter=False))
            if "talent_3_10" in self.talents:
                zafu_dice_list.append(Dice(5, 7, DiceType.BLOCK, is_counter=True))

            card_zafu_block = Card(
                id="zafu_block_card", name="Зафу: Оборона", tier=1, card_type="melee",
                description="Неизменяемая защита.", flags=["unchangeable"],
                dice_list=zafu_dice_list
            )

            if self.computed_speed_dice:
                d_min, d_max = self.computed_speed_dice[0]
            else:
                d_min, d_max = self.base_speed_min, self.base_speed_max

            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")
            val_spd = max(1, random.randint(d_min, d_max) + mod)

            self.active_slots.append({
                'speed': val_spd, 'card': card_zafu_block, 'target_slot': None, 'is_aggro': False,
                'source_effect': 'Defense 🛡️', 'locked': True
            })

    def is_staggered(self) -> bool:
        if self.get_status("red_lycoris") > 0:
            return False
        return self.current_stagger <= 0

    def is_dead(self) -> bool:
        if self.get_status("red_lycoris") > 0:
            return False
        return self.current_hp <= 0

    def tick_cooldowns(self):
        for k in list(self.cooldowns.keys()):
            self.cooldowns[k] -= 1
            if self.cooldowns[k] <= 0: del self.cooldowns[k]

        for k in list(self.active_buffs.keys()):
            self.active_buffs[k] -= 1
            if self.active_buffs[k] <= 0: del self.active_buffs[k]

        for cid in list(self.card_cooldowns.keys()):
            self.card_cooldowns[cid] -= 1
            if self.card_cooldowns[cid] <= 0:
                del self.card_cooldowns[cid]

        if self.is_dead():
            self.active_buffs.clear()
            self.card_cooldowns.clear()