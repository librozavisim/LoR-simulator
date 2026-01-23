import os
import json
import streamlit as st
from collections import Counter

BUILDS_DIR = "data/builds"

def ensure_builds_dir():
    if not os.path.exists(BUILDS_DIR):
        os.makedirs(BUILDS_DIR)

def save_build(name, deck_ids):
    ensure_builds_dir()
    path = os.path.join(BUILDS_DIR, f"{name}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(deck_ids, f, indent=2, ensure_ascii=False)
        st.success(f"Сборка '{name}' успешно сохранена!")
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

def load_build_ids(filename):
    path = os.path.join(BUILDS_DIR, filename)
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return []

def get_card_source_files():
    """Возвращает список файлов .json из папки data/cards"""
    path = "data/cards"
    if not os.path.exists(path): return []
    return sorted([f for f in os.listdir(path) if f.endswith(".json")])

def load_ids_from_source(filename):
    """Извлекает ID всех карт из файла источника"""
    path = os.path.join("data/cards", filename)
    ids = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            cards = data.get("cards", []) if isinstance(data, dict) else data
            if isinstance(cards, list):
                for c in cards:
                    if isinstance(c, dict) and "id" in c:
                        ids.append(c["id"])
    except Exception as e:
        st.error(f"Ошибка чтения файла источника: {e}")
    return ids

def force_update_deck_ui(u_key, new_deck_ids, all_valid_ids):
    """Принудительно обновляет session_state для UI."""
    valid_new_ids = [cid for cid in new_deck_ids if cid in all_valid_ids]
    unique_ids = list(set(valid_new_ids))
    st.session_state[f"deck_sel_{u_key}"] = unique_ids

    counts = Counter(valid_new_ids)
    for cid, qty in counts.items():
        safe_qty = max(1, min(3, qty))
        st.session_state[f"qty_{u_key}_{cid}"] = safe_qty

    return valid_new_ids