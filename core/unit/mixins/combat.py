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

        # 1. Основные кубики
        for (d_min, d_max) in self.computed_speed_dice:
            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")
            val = max(1, random.randint(d_min, d_max) + mod)
            self.active_slots.append({
                'speed': val, 'card': None, 'target_slot': None, 'is_aggro': False
            })

        # 2. Активные способности (Ярость)
        if self.active_buffs.get("berserker_rage", 0) > 0:
            d_min, d_max = self.computed_speed_dice[0] if self.computed_speed_dice else (self.base_speed_min, self.base_speed_max)
            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")
            val = max(1, random.randint(d_min, d_max) + mod)

            self.active_slots.append({
                'speed': val, 'card': None, 'target_slot': None, 'is_aggro': False,
                'source_effect': 'Rage 😡'
            })

        # 3. ТАЛАНТ: НЕИСТОВСТВО (Frenzy)
        if "frenzy" in self.talents:
            if self.computed_speed_dice:
                d_min, d_max = self.computed_speed_dice[0]
            else:
                d_min, d_max = self.base_speed_min, self.base_speed_max

            mod = self.get_status("haste") - self.get_status("slow") - self.get_status("bind")

            # --- Слот 1: Контр-кубик (5-7) ---
            val1 = max(1, random.randint(d_min, d_max) + mod)
            card_frenzy_1 = Card(
                id="frenzy_counter_1", name="Counter (5-7)", tier=1, card_type="melee",
                description="Counter Die: Перехватывает односторонние атаки.",
                dice_list=[Dice(5, 7, DiceType.SLASH, is_counter=True)]
            )
            self.active_slots.append({
                'speed': val1, 'card': card_frenzy_1, 'target_slot': None, 'is_aggro': False,
                'source_effect': 'Counter ⚡', 'locked': True
            })

            # --- Слот 2: Если Self-Control > 10 (6-8) ---
            if self.get_status("self_control") > 10:
                val2 = max(1, random.randint(d_min, d_max) + mod)
                card_frenzy_2 = Card(
                    id="frenzy_counter_2", name="Counter II (6-8)", tier=2, card_type="melee",
                    description="Counter Die: Перехватывает односторонние атаки.",
                    dice_list=[Dice(6, 8, DiceType.SLASH, is_counter=True)]
                )
                self.active_slots.append({
                    'speed': val2, 'card': card_frenzy_2, 'target_slot': None, 'is_aggro': False,
                    'source_effect': 'Counter+ ⚡', 'locked': True
                })

        # 4. СТАТУС: Red Lycoris
        if self.get_status("red_lycoris") > 0:
            for slot in self.active_slots:
                slot['prevent_redirection'] = True
                if not slot.get('source_effect'):
                    slot['source_effect'] = "Lycoris 🩸"

        # 5. ТАЛАНТ: МАХНУТЬ ХВОСТИКОМ
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

        # 6. ТАЛАНТ: ОБОРОНА (ZAFU)
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