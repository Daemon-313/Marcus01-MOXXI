"""Classify natural-language questions about MARCUS-01."""

import re


HEIGHT_PATTERNS = (
    r"\bhow tall (?:will|would|is) it be\b",
    r"\bhow tall is it\b",
    r"\bwhat(?:'s| is) its height\b",
    r"\bhow high will it stand\b",
    r"\bhow big is it\b",
    r"\bhow tall will you be\b",
    r"\bhow high will you stand\b",
    r"\bwhat(?:'s| is) your planned height\b",
    r"\bhow tall are you going to be\b",
    r"\bwhat about your height\b",
    r"\bwhat about its height\b",
    r"\bhow big are you going to be\b",
)

MOVEMENT_PATTERNS = (
    r"\b(?:will|does) it have wheels\b",
    r"\bhow will it move\b",
    r"\bhow does it move\b",
    r"\bhow will it get around\b",
    r"\bhow are you going to get around\b",
    r"\bhow will you get around\b",
    r"\bhow will you move\b",
    r"\bhow will you drive\b",
    r"\bwill you be able to drive around\b",
    r"\bwhat will you use to move\b",
    r"\bwill you have wheels\b",
    r"\bhow are you going to move\b",
)

WHEEL_SELECTION_PATTERNS = (
    r"\bwhat kind of wheels will it have\b",
    r"\bwhat wheels will it use\b",
    r"\bare your wheels picked out yet\b",
    r"\bwhat kind of wheels are you getting\b",
    r"\bhave you picked your wheels yet\b",
    r"\bwhat kind of wheels will you have\b",
    r"\bwhat about the wheels\b",
)

COMPLETION_PATTERNS = (
    r"\bwhen will it be ready\b",
    r"\bwhen will you be ready\b",
    r"\bdo you know when you(?:'ll| will) be finished\b",
    r"\bwhen do you think you(?:'ll| will) be built\b",
    r"\bwhen will you be finished\b",
    r"\bwhen will it be finished\b",
    r"\bhow long until you(?:'re| are) built\b",
)


def classify_robot_question(message):
    """Return a robot-question category or None."""

    if not isinstance(message, str):
        return None

    text = message.casefold().strip()

    if not text:
        return None

    categories = (
        ("height", HEIGHT_PATTERNS),
        ("wheel_selection", WHEEL_SELECTION_PATTERNS),
        ("movement", MOVEMENT_PATTERNS),
        ("completion", COMPLETION_PATTERNS),
    )

    for category, patterns in categories:
        if any(re.search(pattern, text) for pattern in patterns):
            return category

    return None
