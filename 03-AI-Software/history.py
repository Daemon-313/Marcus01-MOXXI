from topics import topic_matches
from datetime import datetime
from pathlib import Path
import json

HISTORY_FILE = Path(__file__).parent / "conversation_history.json"


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_history(history):
    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def record_exchange(user_message, moxxi_response):
    history = load_history()

    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user": user_message,
        "moxxi": moxxi_response
    })

    save_history(history)
    return len(history)


def get_recent_history(limit=5):
    return load_history()[-limit:]


def search_history(query, limit=5):
    """Find saved exchanges containing the query."""
    if not isinstance(query, str) or not query.strip():
        return []

    if not isinstance(limit, int) or limit <= 0:
        return []

    query = query.casefold().strip()
    matches = []

    for entry in reversed(load_history()):
        if not isinstance(entry, dict):
            continue

        user_text = str(entry.get("user", ""))
        moxxi_text = str(entry.get("moxxi", ""))

        if query in user_text.casefold() or query in moxxi_text.casefold():
            matches.append(entry)

        if len(matches) >= limit:
            break

    return matches


def search_conversations(topic, mode="user"):
    """Search original messages or both sides of a conversation."""
    topic = topic.lower().strip()

    if not topic:
        return []

    if mode not in ("user", "both"):
        raise ValueError("mode must be 'user' or 'both'")

    recall_prefixes = (
        "what did i say about",
        "what did we talk about",
        "do you remember when i said",
    )

    matches = []

    for entry in load_history():
        user_text = entry.get("user", "")
        moxxi_text = entry.get("moxxi", "")

        if not isinstance(user_text, str):
            continue

        if not isinstance(moxxi_text, str):
            moxxi_text = ""

        if user_text.lower().strip().startswith(recall_prefixes):
            continue

        user_match = topic_matches(topic, user_text)
        response_match = topic_matches(topic, moxxi_text)

        if user_match or (mode == "both" and response_match):
            matches.append(entry)

    return matches
