import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"


def load_memory():
    if MEMORY_FILE.exists():
        try:
            with MEMORY_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
        except (OSError, json.JSONDecodeError):
            print("MOXXI: My memory file needs attention, sugar.")

    return {"user_name": None, "conversations": 0}


def save_memory(memory):
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)
