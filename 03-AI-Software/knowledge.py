from pathlib import Path
import json
import os
import tempfile

KNOWLEDGE_FILE = Path(__file__).resolve().parent / "knowledge.json"

DEFAULT_KNOWLEDGE = {
    "schema_version": 1,
    "robot": {},
    "hardware": {},
    "software": {},
    "design_decisions": [],
    "project_milestones": [],
    "learned_facts": []
}


def load_knowledge():
    """Load structured knowledge without modifying the file."""
    if not KNOWLEDGE_FILE.exists():
        return {
            key: value.copy() if isinstance(value, (dict, list)) else value
            for key, value in DEFAULT_KNOWLEDGE.items()
        }

    with KNOWLEDGE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Knowledge file must contain a JSON object.")

    return data


def save_knowledge(knowledge):
    """Validate and atomically save structured knowledge."""
    if not isinstance(knowledge, dict):
        raise TypeError("Knowledge must be a dictionary.")

    required = set(DEFAULT_KNOWLEDGE)

    if not required.issubset(knowledge):
        raise ValueError("Knowledge is missing required fields.")

    for category in ("robot", "hardware", "software"):
        if not isinstance(knowledge[category], dict):
            raise TypeError(f"{category} must be a dictionary.")

    for category in (
        "design_decisions",
        "project_milestones",
        "learned_facts"
    ):
        if not isinstance(knowledge[category], list):
            raise TypeError(f"{category} must be a list.")

    serialized = json.dumps(
        knowledge,
        indent=4,
        ensure_ascii=False
    )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=KNOWLEDGE_FILE.parent,
            prefix=".knowledge_",
            suffix=".tmp",
            delete=False
        ) as file:
            temp_path = Path(file.name)
            file.write(serialized)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_path, KNOWLEDGE_FILE)

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def get_knowledge(category, key=None):
    """Retrieve a category or a specific knowledge value."""
    knowledge = load_knowledge()
    value = knowledge.get(category)

    if key is None:
        return value

    if isinstance(value, dict):
        return value.get(key)

    return None


def find_robot_fact(category, key):
    """Retrieve a specific stored robot fact."""
    if not isinstance(category, str) or not isinstance(key, str):
        return None

    category = category.strip()
    key = key.strip()

    if not category or not key:
        return None

    knowledge = load_knowledge()
    section = knowledge.get(category)

    if not isinstance(section, dict):
        return None

    return section.get(key)

