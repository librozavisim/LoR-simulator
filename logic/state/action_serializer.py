class ActionSerializer:
    @staticmethod
    def _find_unit_index(unit, team_left, team_right):
        if unit in team_left: return "left", team_left.index(unit)
        if unit in team_right: return "right", team_right.index(unit)
        return None, -1

    @staticmethod
    def _get_unit_by_index(ref, team_left, team_right):
        side, idx = ref
        if idx == -1: return None
        if side == "left" and 0 <= idx < len(team_left): return team_left[idx]
        if side == "right" and 0 <= idx < len(team_right): return team_right[idx]
        return None

    @staticmethod
    def serialize_actions(actions, team_left, team_right):
        serialized = []
        for act in actions:
            src_side, src_idx = ActionSerializer._find_unit_index(act['source'], team_left, team_right)
            tgt_side, tgt_idx = ActionSerializer._find_unit_index(act['target_unit'], team_left, team_right)

            serialized.append({
                "source_ref": [src_side, src_idx],
                "target_ref": [tgt_side, tgt_idx],
                "source_idx": act['source_idx'],
                "target_slot_idx": act['target_slot_idx'],
                "score": act['score'],
                "is_left": act['is_left'],
                "card_type": act['card_type'],
                "slot_meta": {
                    "speed": act['slot_data'].get('speed'),
                    "is_aggro": act['slot_data'].get('is_aggro'),
                    "destroy_on_speed": act['slot_data'].get('destroy_on_speed')
                }
            })
        return serialized

    @staticmethod
    def restore_actions(serialized_actions, team_left, team_right):
        restored = []
        for s_act in serialized_actions:
            source = ActionSerializer._get_unit_by_index(s_act['source_ref'], team_left, team_right)
            target = ActionSerializer._get_unit_by_index(s_act['target_ref'], team_left, team_right)

            if not source: continue

            slot_idx = s_act['source_idx']
            real_slot = None
            if 0 <= slot_idx < len(source.active_slots):
                real_slot = source.active_slots[slot_idx]
            if not real_slot: continue

            opposing_team = team_right if s_act['is_left'] else team_left
            restored.append({
                'source': source,
                'source_idx': slot_idx,
                'target_unit': target,
                'target_slot_idx': s_act['target_slot_idx'],
                'slot_data': real_slot,
                'score': s_act['score'],
                'is_left': s_act['is_left'],
                'card_type': s_act['card_type'],
                'opposing_team': opposing_team
            })
        return restored