"""Respond to follow-up questions about MOXXI's systems."""

import re

from voice_settings import load_voice_settings


def respond_with_multitopic_context(message, context):
    """Answer a supported follow-up for the active topic."""

    if not isinstance(message, str) or context is None:
        return None

    text = message.casefold().strip().rstrip("?.!")

    topic = context.get_topic()

    introductions = {
        "tell me about your voice": (
            "My voice system lets me speak using offline "
            "speech engines, sugar! We're developing it "
            "to give me a warm, playful personality."
        ),
        "tell me about your memory": (
            "My memory system helps me remember your saved "
            "name and search our conversation history, "
            "darling. We're expanding it step by step."
        ),
        "tell me about your software": (
            "I'm powered by Python software, sugar! "
            "My conversation engine connects my knowledge, "
            "memory, personality, and voice systems."
        ),
    }

    introduction = introductions.get(text)
    if introduction is not None:
        return introduction

    introduction_patterns = {
        "voice": (
            r"^(?:can you )?tell me about your voice$",
            r"^i(?:'d| would) like to know about your voice$",
            r"^explain your voice(?: system)?$",
            r"^what about your voice$",
        ),
        "memory": (
            r"^(?:can you )?tell me about your memory$",
            r"^i(?:'d| would) like to know about your memory$",
            r"^explain your memory(?: system)?$",
            r"^what about your memory$",
        ),
        "software": (
            r"^(?:can you )?tell me about your software$",
            r"^i(?:'d| would) like to know about your software$",
            r"^explain your software(?: system)?$",
            r"^what about your software$",
        ),
    }

    for subject, patterns in introduction_patterns.items():
        if topic != subject:
            continue

        if any(re.search(pattern, text) for pattern in patterns):
            return introductions[f"tell me about your {subject}"]

    if topic == "voice":
        if re.search(
            r"\b(?:which|what) voice are you using\b", text
        ):
            settings = load_voice_settings()
            engine = settings.get("engine", "windows")

            if not settings.get("enabled", True):
                return "My voice output is currently disabled, sugar."

            if engine == "piper":
                return (
                    "I'm configured to use Piper Amy, darling! "
                    "She's my current offline voice."
                )

            if engine == "windows":
                return (
                    "I'm configured to use my Windows speech "
                    "engine right now, sugar."
                )

            return "I couldn't identify my configured voice engine."

        if re.search(r"\bcan you speak offline\b", text):
            return (
                "You bet, sugar! My speech system can run "
                "locally without an internet connection."
            )

    if topic == "memory":
        if re.search(r"\bwhat can you remember\b", text):
            return (
                "I can remember your saved name and search "
                "our recorded conversations, darling. "
                "My memory system is still growing."
            )

        if re.search(
            r"\bdo you save our conversations\b", text
        ):
            return (
                "Yes, sugar. My conversation history system "
                "can save our exchanges locally."
            )

    if topic == "software":
        if re.search(
            r"\bwhat language are you written in\b", text
        ):
            return (
                "I'm written primarily in Python, darling! "
                "That's what powers my conversation and "
                "memory systems."
            )

        if re.search(
            r"\bcan you control the robot yet\b", text
        ):
            return (
                "Not yet, sugar. My physical robot controls "
                "are still on our development roadmap."
            )

    # Context-aware follow-ups for everyday topics.
    if topic == "laptop":
        if text in ("battery life", "the battery life"):
            context.set_subtopic("battery_life")
            return (
                "Gotcha, sugar! Are you having trouble "
                "with how long your laptop lasts between charges?"
            )

        if (
            context.get_subtopic() == "battery_life"
            and text in (
                "how can i improve it",
                "how do i improve it",
                "how can i make it last longer",
            )
        ):
            return (
                "To improve your laptop's battery life, sugar, "
                "try lowering screen brightness, using battery "
                "saver mode, and closing unnecessary background "
                "applications."
            )

        if re.fullmatch(r"(?:and )?(?:what about (?:its|the) battery|how['’]s its battery|tell me about its battery)", text):
            return (
                "Your laptop's battery, sugar? "
                "Are we looking at battery life, charging, "
                "or replacing it?"
            )

    if topic == "car":
        if re.fullmatch(r"(?:and )?(?:what about (?:the|its) wheels|how about the tires)", text):
            return (
                "Your car's wheels, darling? "
                "Are you thinking about tires, wheel sizes, "
                "or something else?"
            )

        if re.fullmatch(r"(?:and )?(?:its engine|tell me about its engine)", text):
            return (
                "What would you like to know about "
                "your car's engine, sugar?"
            )

    return None
