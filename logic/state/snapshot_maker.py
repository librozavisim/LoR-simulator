from logic.state.action_serializer import ActionSerializer

class SnapshotMaker:
    @staticmethod
    def get_state_snapshot(session_state):
        """Создает ПОЛНЫЙ слепок состояния (Keyframe)."""
        return {
            "type": "full",
            "page": session_state.get("nav_page", "⚔️ Simulator"),

            "team_left_data": [u.to_dict() for u in session_state.get('team_left', [])],
            "team_right_data": [u.to_dict() for u in session_state.get('team_right', [])],

            "phase": session_state.get('phase', 'roll'),
            "round_number": session_state.get('round_number', 1),
            "turn_message": session_state.get('turn_message', ""),
            "battle_logs": session_state.get('battle_logs', []),
            "script_logs": session_state.get('script_logs', ""),

            "turn_phase": session_state.get('turn_phase', 'planning'),
            "action_idx": session_state.get('action_idx', 0),
            "executed_slots": list(session_state.get('executed_slots', [])),

            "turn_actions": ActionSerializer.serialize_actions(
                session_state.get('turn_actions', []),
                session_state.get('team_left', []),
                session_state.get('team_right', [])
            ),

            "profile_unit": session_state.get("profile_selected_unit"),
            "leveling_unit": session_state.get("leveling_selected_unit"),
            "tree_unit": session_state.get("tree_selected_unit"),
            "checks_unit": session_state.get("checks_selected_unit"),
        }

    @staticmethod
    def get_dynamic_snapshot(session_state):
        """Создает ДИНАМИЧЕСКИЙ слепок (Delta)."""
        return {
            "type": "dynamic",
            "team_left_dyn": [u.get_dynamic_state() for u in session_state.get('team_left', [])],
            "team_right_dyn": [u.get_dynamic_state() for u in session_state.get('team_right', [])],

            "phase": session_state.get('phase', 'roll'),
            "round_number": session_state.get('round_number', 1),
            "turn_message": session_state.get('turn_message', ""),
            "battle_logs": session_state.get('battle_logs', []),

            "turn_actions": ActionSerializer.serialize_actions(
                session_state.get('turn_actions', []),
                session_state.get('team_left', []),
                session_state.get('team_right', [])
            ),

            "turn_phase": session_state.get('turn_phase', 'planning'),
            "action_idx": session_state.get('action_idx', 0),
            "executed_slots": list(session_state.get('executed_slots', [])),
        }