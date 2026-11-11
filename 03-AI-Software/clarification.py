"""Ask for clarification when a question lacks context."""

import re


def respond_with_clarification(message, context):
    """Return a clarification question or None."""

    if not isinstance(message, str):
        return None

    if context is None:
        return None

    # Robot follow-ups are handled by the robot context system.
    # Other topics do not establish what an ambiguous "it" means.
    if context.get_topic() == "robot":
        return None

    text = message.casefold().strip().rstrip("?.!")

    height_patterns = (
        r"^how tall (?:will|would|is) it be$",
        r"^how tall is it$",
        r"^what(?:'s| is) its height$",
        r"^how high will it stand$",
        r"^how big is it$",
    )

    if any(re.search(pattern, text) for pattern in height_patterns):
        return (
            "What are we measuring, sugar? "
            "MARCUS-01, or something else?"
        )

    movement_patterns = (
        r"^(?:will|does) it have wheels$",
        r"^how will it move$",
        r"^how does it move$",
        r"^what kind of wheels will it have$",
        r"^what wheels will it use$",
        r"^how will it get around$",
    )

    if any(re.search(pattern, text) for pattern in movement_patterns):
        return (
            "Which machine are we talking about, darling? "
            "MARCUS-01 or something else?"
        )

    if re.search(r"^when will it be ready$", text):
        return (
            "Which project do you mean, sugar? "
            "MARCUS-01, or something else?"
        )

    return None
