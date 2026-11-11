"""Recognize common MOXXI conversation intents."""

import re


INTENT_PATTERNS = {
    "identity": [
        r"\bwhat(?:'s| is) your name\b",
        r"\bwho are you\b",
        r"\btell me about yourself\b",
        r"\btell me about you\b",
        r"\bdescribe yourself\b",
    ],
    "purpose": [
        r"\bwhat(?:'s| is) your purpose\b",
        r"\bwhat is your purpose\b",
        r"\bwhy were you created\b",
        r"\bwhat(?:'s| is) your job\b",
        r"\bwhat are you supposed to do\b",
    ],
    "capabilities": [
        r"\bwhat can you do\b",
        r"\bwhat are your capabilities\b",
        r"\bwhat are you capable of\b",
        r"\bwhat features do you have\b",
    ],
    "body": [
        r"\bdo you have a body\b",
        r"\bwhere is your body\b",
        r"\bwhat about your body\b",
        r"\bwhen will you have a body\b",
    ],
    "memory": [
        r"\bcan you remember things\b",
        r"\bdo you have memory\b",
        r"\bhow does your memory work\b",
    ],
}


def recognize_intent(message):
    """Return a recognized intent or None."""

    if not isinstance(message, str):
        return None

    text = message.casefold().strip()

    if not text:
        return None

    # Normalize common informal phrasing.
    text = re.sub(r"\bwhats\b", "what's", text)
    text = re.sub(r"\bya\b", "you", text)

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return intent

    return None
