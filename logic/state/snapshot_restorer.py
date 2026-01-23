from core.unit.unit import Unit
from logic.state.action_serializer import ActionSerializer


class SnapshotRestorer:
    @staticmethod
    def _restore_teams_from_full(data):
        l_data = data.get("team_left_data", [])
        r_data = data.get("team_right_data", [])

        team_left = []
        for d in l_data:
            try:
                team_left.append(Unit.from_dict(d))
            except Exception as e:
                print(f"Error restoring left: {e}")

        team_right = []
        for d in r_data:
            try:
                team_right.append(Unit.from_dict(d))
            except Exception as e:
                print(f"Error restoring right: {e}")

        return team_left, team_right

    @staticmethod
    def restore_from_dynamic(session_state, dynamic_data, base_data):
        # 1. Base
        team_left, team_right = SnapshotRestorer._restore_teams_from_full(base_data)

        # 2. Delta
        l_dyn = dynamic_data.get("team_left_dyn", [])
        r_dyn = dynamic_data.get("team_right_dyn", [])

        for i, u in enumerate(team_left):
            if i < len(l_dyn): u.apply_dynamic_state(l_dyn[i])

        for i, u in enumerate(team_right):
            if i < len(r_dyn): u.apply_dynamic_state(r_dyn[i])

        for u in team_left + team_right: u.recalculate_stats()

        session_state['team_left'] = team_left
        session_state['team_right'] = team_right

        SnapshotRestorer._restore_common_fields(session_state, dynamic_data)

        # Restore actions
        raw_actions = dynamic_data.get('turn_actions', [])
        session_state['turn_actions'] = ActionSerializer.restore_actions(raw_actions, team_left,
                                                                         team_right) if raw_actions else []
        session_state['teams_loaded'] = True

    @staticmethod
    def restore_from_full(session_state, data):
        team_left, team_right = SnapshotRestorer._restore_teams_from_full(data)

        for u in team_left + team_right: u.recalculate_stats()

        session_state['team_left'] = team_left
        session_state['team_right'] = team_right

        SnapshotRestorer._restore_common_fields(session_state, data)
        session_state['script_logs'] = data.get('script_logs', "")

        # Selectors
        mapping = {
            "profile_unit": "profile_selected_unit",
            "leveling_unit": "leveling_selected_unit",
            "tree_unit": "tree_selected_unit",
            "checks_unit": "checks_selected_unit",
        }
        for k, v in mapping.items():
            if data.get(k): session_state[v] = data[k]

        try:
            session_state['nav_page'] = data.get("page", "⚔️ Simulator")
        except:
            pass

        if "undo_stack" in data: session_state['undo_stack'] = data["undo_stack"]

        raw_actions = data.get('turn_actions', [])
        session_state['turn_actions'] = ActionSerializer.restore_actions(raw_actions, team_left,
                                                                         team_right) if raw_actions else []
        session_state['teams_loaded'] = True

    @staticmethod
    def _restore_common_fields(session_state, data):
        session_state['phase'] = data.get('phase', 'roll')
        session_state['round_number'] = data.get('round_number', 1)
        session_state['turn_message'] = data.get('turn_message', "")
        session_state['battle_logs'] = data.get('battle_logs', [])
        session_state['turn_phase'] = data.get('turn_phase', 'planning')
        session_state['action_idx'] = data.get('action_idx', 0)

        session_state['executed_slots'] = set()
        for item in data.get('executed_slots', []):
            session_state['executed_slots'].add(tuple(item))