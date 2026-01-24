from core.logging import logger, LogLevel
from logic.battle_flow.clash.clash import process_clash
from logic.battle_flow.interactions import resolve_interaction
from logic.battle_flow.onesided.onesided import process_onesided
from logic.mechanics.clash_mechanics import ClashMechanicsMixin


class ClashFlowMixin(ClashMechanicsMixin):
    """
    Связующий слой. Передает 'self' (engine) в функции логики.
    """

    def _resolve_card_clash(self, attacker, defender, round_label, is_left, spd_a, spd_d, intent_a=True, intent_d=True):
        logger.log(f"Resolving Clash: {attacker.name} vs {defender.name} (Spd: {spd_a}/{spd_d})", LogLevel.VERBOSE, "Flow")
        return process_clash(self, attacker, defender, round_label, is_left, spd_a, spd_d, intent_a, intent_d)

    # Добавили intent_atk
    def _resolve_one_sided(self, source, target, round_label, spd_atk, spd_def, intent_atk=True, is_redirected=False):
        logger.log(f"Resolving One-Sided: {source.name} -> {target.name} (Spd: {spd_atk}/{spd_def})", LogLevel.VERBOSE, "Flow")
        return process_onesided(self, source, target, round_label, spd_atk, spd_def, intent_atk, is_redirected)

    def _resolve_clash_interaction(self, winner_ctx, loser_ctx, diff):
        logger.log(f"Resolving Interaction: Winner {winner_ctx.source.name} (Diff: {diff})", LogLevel.VERBOSE, "Flow")
        return resolve_interaction(self, winner_ctx, loser_ctx, diff)

    def _find_counter_die(self, unit):
        """Ищет первый доступный слот с картой, содержащей is_counter=True."""
        for i, slot in enumerate(unit.active_slots):
            if slot.get('consumed', False): continue
            card = slot.get('card')
            if card and card.dice_list:
                # Берем первый кубик
                first_die = card.dice_list[0]
                if getattr(first_die, 'is_counter', False):
                    logger.log(f"Found Counter Die for {unit.name} at slot {i}", LogLevel.VERBOSE, "Flow")
                    return i, first_die
        return -1, None

    def _consume_counter_die(self, unit, slot_idx):
        if 0 <= slot_idx < len(unit.active_slots):
            unit.active_slots[slot_idx]['consumed'] = True
            logger.log(f"Consumed Counter Die for {unit.name} at slot {slot_idx}", LogLevel.NORMAL, "Flow")