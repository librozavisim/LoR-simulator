from core.logging import logger, LogLevel


class CooldownsMixin:
    """
    Управление кулдаунами карт и способностей.
    """

    def tick_cooldowns(self):
        # Удаляем истекшие кулдауны способностей
        self.cooldowns = {k: v - 1 for k, v in self.cooldowns.items() if v > 1}
        self.active_buffs = {k: v - 1 for k, v in self.active_buffs.items() if v > 1}

        # Логика для списков кулдаунов карт (поддержка нескольких копий одной карты)
        new_card_cds = {}
        if hasattr(self, 'card_cooldowns') and self.card_cooldowns:
            for cid, timers in self.card_cooldowns.items():
                if isinstance(timers, int): timers = [timers]

                new_timers = [t - 1 for t in timers if t > 1]
                if new_timers:
                    new_card_cds[cid] = new_timers

        self.card_cooldowns = new_card_cds

        if self.is_dead():
            self.active_buffs.clear()
            self.card_cooldowns.clear()
            logger.log(f"{self.name} died, Cooldowns/Buffs cleared.", LogLevel.NORMAL, "System")

        logger.log(f"{self.name} cooldowns ticked.", LogLevel.VERBOSE, "System")