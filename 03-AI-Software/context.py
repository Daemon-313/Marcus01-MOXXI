"""Track the active subject of a MOXXI conversation."""
from robot_questions import classify_robot_question

import re


class ConversationContext:
    """Keep a temporary conversation topic in memory."""

    def __init__(self):
        self.active_topic = None

    def update(self, message):
        """Recognize an explicitly mentioned topic."""

        if not isinstance(message, str):
            return self.active_topic

        text = message.casefold().strip()

        # Clear outdated context when the user explicitly
        # changes or ends the current subject.
        topic_changes = (
            "let's talk about something else",
            "lets talk about something else",
            "change the subject",
            "change topic",
            "new topic",
            "forget that topic",
            "something else",
        )

        if any(text.startswith(phrase) for phrase in topic_changes):
            self.clear()
            return self.active_topic

        # Explicit questions about MOXXI's planned physical body
        # can establish the robot topic independently.
        robot_question = classify_robot_question(message)

        explicit_robot_questions = {
            "how tall will you be",
            "what about your height",
            "how tall are you going to be",
            "how big are you going to be",
            "how high will you stand",
            "what's your planned height",
            "what is your planned height",
            "how will you move",
            "will you have wheels",
            "how are you going to move",
            "how will you drive",
            "how will you get around",
            "how are you going to get around",
            "will you be able to drive around",
            "what will you use to move",
            "have you picked your wheels yet",
            "what kind of wheels will you have",
            "are your wheels picked out yet",
            "what kind of wheels are you getting",
            "when will you be ready",
            "when will you be finished",
            "how long until you're built",
            "when do you think you'll be built",
            "do you know when you'll be finished",
            "do you know when you will be finished",
        }

        if (
            robot_question is not None
            and text.rstrip("?.!") in explicit_robot_questions
        ):
            self.active_topic = "robot"
            return self.active_topic

        robot_terms = (
            "robot",
            "marcus-01",
            "marcus01",
            "robotic body",
            "your body",
        )

        # Robot-control questions can be software follow-ups.
        if (
            self.active_topic == "software"
            and text.rstrip("?.!") == "can you control the robot yet"
        ):
            return self.active_topic

        if any(term in text for term in robot_terms):
            self.active_topic = "robot"
            return self.active_topic

        topic_terms = {
            "voice": (
                "your voice",
                "which voice are you using",
                "what voice are you using",
                "piper amy",
                "speech engine",
                "text to speech",
                "voice system",
            ),
            "memory": (
                "your memory",
                "your memories",
                "remember things",
                "conversation history",
                "memory system",
            ),
            "software": (
                "your software",
                "what language are you written in",
                "your programming",
                "your code",
                "python code",
                "ai software",
            ),
        }

        for topic, terms in topic_terms.items():
            if any(term in text for term in terms):
                self.active_topic = topic
                return self.active_topic

        return self.active_topic

    def get_topic(self):
        """Return the current conversation topic."""
        return self.active_topic

    def clear(self):
        """Forget the current conversation topic."""
        self.active_topic = None

    def is_robot_followup(self, message):
        """Detect robot follow-ups using the shared classifier."""

        if self.active_topic != "robot":
            return False

        return classify_robot_question(message) is not None
