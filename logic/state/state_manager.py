from logic.state.file_manager import StateFileManager
from logic.state.snapshot_maker import SnapshotMaker
from logic.state.snapshot_restorer import SnapshotRestorer
from logic.state.action_serializer import ActionSerializer


class StateManager:
    """
    Фасад для управления состоянием.
    Делегирует задачи специализированным модулям.
    """

    # === File Ops ===
    ensure_dir = StateFileManager.ensure_dir
    get_available_states = StateFileManager.get_available_states
    create_new_state = StateFileManager.create_new_state
    delete_state = StateFileManager.delete_state
    load_state = StateFileManager.load_json

    @staticmethod
    def save_state(session_state, filename="default"):
        data = SnapshotMaker.get_state_snapshot(session_state)
        data["undo_stack"] = session_state.get("undo_stack", [])
        StateFileManager.save_json(data, filename)

    # === Snapshots ===
    get_state_snapshot = SnapshotMaker.get_state_snapshot
    get_dynamic_snapshot = SnapshotMaker.get_dynamic_snapshot

    restore_state_from_snapshot = SnapshotRestorer.restore_from_full
    restore_from_dynamic_snapshot = SnapshotRestorer.restore_from_dynamic

    # === Helpers (проброс для совместимости) ===
    restore_actions = ActionSerializer.restore_actions
    _serialize_actions = ActionSerializer.serialize_actions