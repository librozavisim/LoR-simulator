from core.logging import logger, LogLevel

class StatusCheckMixin:
    """
    Проверки статусов с учетом иммунитетов от механик.
    """

    def is_staggered(self) -> bool:
        if self.current_stagger > 0:
            return False

        # Проверяем иммунитет к оглушению
        for effect in self._iter_all_mechanics():
            attr = getattr(effect, "prevents_stagger", None)
            if callable(attr):
                if attr(self):
                    logger.log(f"{self.name} stagger prevented by {getattr(effect, 'id', 'Effect')}", LogLevel.NORMAL, "Immunity")
                    return False
            elif attr:
                return False

        return True

    def is_dead(self) -> bool:
        """Проверяет, мертв ли юнит, учитывая бессмертие."""
        if self.current_hp > 0:
            return False

        # Проверяем иммунитет к смерти
        for effect in self._iter_all_mechanics():
            attr = getattr(effect, "prevents_death", None)
            if callable(attr):
                if attr(self):
                    logger.log(f"{self.name} death prevented by {getattr(effect, 'id', 'Effect')}", LogLevel.NORMAL, "Immunity")
                    return False
            elif attr:
                return False

        return True

    def is_immune_to_surprise_attack(self) -> bool:
        """Проверяет, имеет ли юнит иммунитет к внезапным атакам."""
        for effect in self._iter_all_mechanics():
            attr = getattr(effect, "prevents_surprise_attack", None)
            if callable(attr):
                if attr(self): return True
            elif attr:
                return True
        return False