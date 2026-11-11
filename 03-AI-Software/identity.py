"""MOXXI identity and self-description responses."""

def respond_with_identity(message):
    """Answer questions about MOXXI's identity and purpose."""

    if not isinstance(message, str):
        return None

    text = message.casefold().strip().rstrip("?.!")

    if text in (
        "tell me about yourself",
        "tell me about you",
        "who are you",
        "describe yourself",
    ):
        return (
            "Well, sugar, I'm MOXXI! "
            "I'm the AI personality behind MARCUS-01, "
            "our mobile robotics project. "
            "Right now, I'm running as software while we build "
            "my future robotic body. "
            "I've got a playful personality, a growing memory, "
            "and plenty of mechanical mischief planned!"
        )

    if text in (
        "what is your purpose",
        "what do you do",
        "what are you for",
    ):
        return (
            "My job is to become the intelligent companion "
            "and control interface for MARCUS-01. "
            "We're developing my voice, memory, conversation "
            "skills, and eventually my ability to interact "
            "with the physical world."
        )

    if text in (
        "what can you do",
        "what are your capabilities",
        "what are you capable of",
    ):
        return (
            "Right now, darling, I can chat using predefined "
            "responses, remember certain information, recall "
            "saved conversations, answer stored robot facts, "
            "and speak using my offline voice system. "
            "More advanced intelligence and robot controls "
            "are still on our development roadmap."
        )

    if text in (
        "do you have a body",
        "where is your body",
        "are you a robot",
    ):
        return (
            "Not quite yet, sugar! "
            "MARCUS-01 is the robotic body we're developing. "
            "For now, I'm software with a voice and attitude. "
            "The wheels and hardware come later!"
        )

    return None
