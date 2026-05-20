import json
from pathlib import Path

HISTORY_PATH = Path("outputs/history.json")


def load_history():
    if not HISTORY_PATH.exists():
        return []

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    HISTORY_PATH.parent.mkdir(exist_ok=True)

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def calculate_delta(current, previous):
    if previous == 0:
        return 0

    return round(((current - previous) / previous) * 100, 1)
