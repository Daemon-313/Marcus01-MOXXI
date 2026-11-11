from clarification_state import ClarificationState
from clarification import respond_with_clarification
from multitopic_responses import respond_with_multitopic_context
from context import ConversationContext
from context_responses import respond_with_context
from intent_responses import respond_with_intent
from identity import respond_with_identity
from history import search_conversations
from history import search_history
from datetime import datetime
from memory import save_memory
from responses import get_response
from topics import topic_matches
_conversation_context = ConversationContext()
_clarification_state = ClarificationState()


def respond(message, memory):
    if not isinstance(message, str):
        return None

    text = message.casefold().strip().rstrip("?.!")

    topic_changes = (
        "new topic",
        "change topic",
        "change the subject",
        "something else",
        "let's talk about something else",
        "lets talk about something else",
        "forget that topic",
    )

    if any(text.startswith(phrase) for phrase in topic_changes):
        _clarification_state.clear()

    pending = _clarification_state.get_pending()

    cancellation_phrases = (
        "never mind",
        "nevermind",
        "actually never mind",
        "actually, never mind",
        "forget it",
        "cancel that",
    )

    if pending is not None and text in cancellation_phrases:
        _clarification_state.clear()
        return (
            "No problem, sugar! "
            "We can talk about something else."
        )

    if pending is not None:
        resolved_question = _clarification_state.resolve(message)

        if resolved_question is not None:
            _conversation_context.update("MARCUS-01")

            resolved_reply = respond_with_context(
                resolved_question, _conversation_context
            )

            if resolved_reply is not None:
                return resolved_reply

        elif text not in ("", "yes", "yeah", "yep"):
            _clarification_state.clear()

    _conversation_context.update(message)

    context_reply = respond_with_context(
        message, _conversation_context
    )

    if context_reply is not None:
        return context_reply

    multitopic_reply = respond_with_multitopic_context(
        message, _conversation_context
    )

    if multitopic_reply is not None:
        return multitopic_reply

    clarification_reply = respond_with_clarification(
        message, _conversation_context
    )
    if clarification_reply is not None:
        _clarification_state.set_pending(message)
        return clarification_reply

    knowledge_reply = respond_with_knowledge(message)
    if knowledge_reply is not None:
        return knowledge_reply

    intent_reply = respond_with_intent(message)
    if intent_reply is not None:
        return intent_reply

    identity_reply = respond_with_identity(message)
    if identity_reply is not None:
        return identity_reply

    text = message.lower().strip()

    if text.rstrip("?.!") in (
        "tell me about marcus-01",
        "tell me about marcus01",
        "tell me about the robot",
    ):
        return (
            "MARCUS-01 is our mobile robotics project, sugar! "
            "He's the future home for my AI personality, "
            "and we're building his hardware and software "
            "in stages."
        )

    recalled = recall_conversation(message)
    if recalled is not None:
        return recalled

    if text.startswith("my name is "):
        user_name = message[11:].strip().rstrip(".!")
        if not user_name:
            return "Tell me your name, darling."

        memory["user_name"] = user_name
        save_memory(memory)
        return f"Well, hello, {user_name}! I'll remember that."

    if "what is my name" in text:
        user_name = memory.get("user_name")
        if user_name:
            return f"Of course I remember you, {user_name}!"
        return "You haven't told me your name yet, sugar."

    if text in ("hello", "hi", "hey"):
        user_name = memory.get("user_name")
        if user_name:
            return f"{get_response('greetings')} Welcome back, {user_name}!"
        return "Well, hello there, sugar! MOXXI is online."

    if "your name" in text:
        return "The name's MOXXI. Your favorite mechanical troublemaker."

    if "how are you" in text:
        return get_response("moods")

    if "time" in text:
        return f"It's {datetime.now():%I:%M %p}, sugar."

    if "date" in text:
        return f"Today's date is {datetime.now():%B %d, %Y}."

    if "robot" in text:
        return "MARCUS-01 is my future home. Just wait until I get wheels!"

    if "help" in text:
        return (
            "Try 'my name is ...', 'what is my name', "
            "'hello', 'time', 'date', or 'robot'."
        )

    return get_response("fallbacks")





def recall_conversation(message):
    """Recall original user messages or shared conversations."""
    text = message.lower().strip()

    prefixes = (
        ("what did i say about", "user"),
        ("what did we talk about", "both"),
        ("do you remember when i said", "user"),
    )

    for prefix, mode in prefixes:
        if not text.startswith(prefix):
            continue

        topic = text[len(prefix):].strip(" ?.!")
        if not topic:
            return "What would you like me to remember, sugar?"

        matches = search_conversations(topic, mode=mode)

        if not matches:
            return (
                f"I couldn't find anything about {topic} "
                "in our saved conversations, sugar."
            )

        recent = matches[-3:]

        if mode == "user":
            messages = [
                entry.get("user", "")
                for entry in recent
            ]
            return "Here's what you told me, sugar: " + " | ".join(messages)

        exchanges = [
            f"You said: {entry.get('user', '')}; "
            f"I replied: {entry.get('moxxi', '')}"
            for entry in recent
        ]

        return "Here's what we discussed, sugar: " + " | ".join(exchanges)

    return None


def respond_with_knowledge(message):
    """Answer supported questions using stored robot knowledge."""
    from knowledge import find_robot_fact

    if not isinstance(message, str):
        return None

    text = message.casefold().strip().rstrip("?.!")

    if text in (
        "how tall is marcus-01",
        "how tall is the robot",
        "what is the robot's height",
    ):
        height = find_robot_fact("robot", "target_height_inches")
        if height is not None:
            return f"MARCUS-01 is designed to stand {height} inches tall, sugar."

    if text in (
        "what is the robot's name",
        "what is the project name",
    ):
        name = find_robot_fact("robot", "project_name")
        if name:
            return f"Our robot is called {name}, darling."

    if text in (
        "what is your ai name",
        "what is the ai's name",
    ):
        name = find_robot_fact("robot", "ai_name")
        if name:
            return f"The name's {name}, sugar!"

    if text in (
        "how many wheels does the robot have",
        "what is the drive configuration",
    ):
        drive = find_robot_fact("hardware", "drive_configuration")
        if drive:
            return f"Our drive configuration is {drive}, darling."

    if text in (
        "does moxxi have voice",
        "is voice enabled",
        "what is the voice status",
    ):
        status = find_robot_fact("software", "voice_interface")
        if status:
            return f"My voice interface status is: {status}, sugar."

    return None

