"""Contextual responses for MOXXI's robot conversations."""

from knowledge import find_robot_fact
from robot_questions import classify_robot_question


def respond_with_context(message, context):
    """Return a contextual robot response or None."""

    if not isinstance(message, str):
        return None

    if context is None:
        return None

    if not context.is_robot_followup(message):
        return None

    category = classify_robot_question(message)

    if category == "height":
        height = find_robot_fact(
            "robot", "target_height_inches"
        )

        if height is not None:
            return (
                f"MARCUS-01 is designed to stand "
                f"{height} inches tall, sugar."
            )

        return "I don't have a confirmed height saved yet, sugar."

    if category in ("movement", "wheel_selection"):
        drive = find_robot_fact(
            "hardware", "drive_configuration"
        )

        if drive:
            drive_text = str(drive).strip()

            if not drive_text:
                return (
                    "I don't have the wheel configuration "
                    "saved yet."
                )

            if category == "wheel_selection":
                return (
                    f"MARCUS-01's planned drive configuration "
                    f"is {drive_text.lower()}, sugar! "
                    "We haven't confirmed a specific wheel "
                    "model in my saved specifications yet."
                )

            return (
                f"MARCUS-01 will move around using "
                f"{drive_text.lower()}, sugar! "
                "That's the drive configuration "
                "we currently have planned."
            )

        return "I don't have the wheel configuration saved yet."

    if category == "completion":
        return (
            "We haven't set a confirmed completion date "
            "for MARCUS-01 yet, sugar. We're developing "
            "the software and hardware in stages."
        )

    return None
