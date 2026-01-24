import glob
import json
import os

STATES_DIR = "data/states"

class StateFileManager:
    @staticmethod
    def ensure_dir():
        if not os.path.exists(STATES_DIR):
            os.makedirs(STATES_DIR, exist_ok=True)
            default_path = os.path.join(STATES_DIR, "default.json")
            if not os.path.exists(default_path):
                with open(default_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    @staticmethod
    def get_available_states():
        StateFileManager.ensure_dir()
        files = glob.glob(os.path.join(STATES_DIR, "*.json"))
        names = [os.path.splitext(os.path.basename(f))[0] for f in files]
        return sorted(names)

    @staticmethod
    def create_new_state(name):
        StateFileManager.ensure_dir()
        filename = f"{name}.json"
        path = os.path.join(STATES_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return True
        return False

    @staticmethod
    def delete_state(name):
        path = os.path.join(STATES_DIR, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    @staticmethod
    def load_json(filename="default"):
        StateFileManager.ensure_dir()
        target_file = os.path.join(STATES_DIR, f"{filename}.json")
        if not os.path.exists(target_file):
            return {}
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_json(data, filename="default"):
        StateFileManager.ensure_dir()
        target_file = os.path.join(STATES_DIR, f"{filename}.json")
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving state to {filename}: {e}")