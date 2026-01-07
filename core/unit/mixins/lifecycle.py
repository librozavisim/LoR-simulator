from logic.calculations.formulas import get_modded_value

class UnitLifecycleMixin:
    def heal_hp(self, amount: int) -> int:
        # Учитываем эффективность лечения (из modifiers)
        final_amt = get_modded_value(amount, "heal_efficiency", self.modifiers)

        # Обработка глубокой раны
        if self.get_status("deep_wound") > 0:
            final_amt = int(final_amt * 0.75)
            self.remove_status("deep_wound", 1)

        self.current_hp = min(self.max_hp, self.current_hp + final_amt)
        return final_amt

    def restore_sp(self, amount: int) -> int:
        if amount <= 0: return 0
        final_sp = min(self.max_sp, self.current_sp + amount)
        recovered = final_sp - self.current_sp
        self.current_sp = final_sp
        return recovered

    def take_sanity_damage(self, amount: int):
        # Паника начинается с 0, но значение может уходить в минус
        self.current_sp = max(-45, self.current_sp - amount)