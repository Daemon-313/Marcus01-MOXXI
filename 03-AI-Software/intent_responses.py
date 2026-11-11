"""Generate responses for recognized MOXXI intents."""

from identity import respond_with_identity
from intents import recognize_intent


CANONICAL_QUESTIONS = {
    "identity": "Tell me about yourself",
    "purpose": "What is your purpose?",
    "capabilities": "What can you do?",
    "body": "Do you have a body?",
}


def respond_with_intent(message):
    """Return an intent-based response or None."""

    intent = recognize_intent(message)

    if intent is None:
        return None

    if intent == "memory":
        return (
            "You bet I can remember things, sugar! "
            "I can save your name, keep a record of our "
            "conversations, and search those records when "
            "you ask me to recall something we've discussed. "
            "My memory is still pretty basic, but we're "
            "working on making it smarter."
        )

    question = CANONICAL_QUESTIONS.get(intent)

    if question is None:
        return None

    return respond_with_identity(question)
