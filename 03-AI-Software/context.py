"""Track the active subject of a MOXXI conversation."""
from robot_questions import classify_robot_question

import re


class ConversationContext:
    """Keep a temporary conversation topic in memory."""

    def __init__(self):
        self.active_topic = None
        self.active_subtopic = None
        self.troubleshooting_step = None
        self.diagnostic_details = {}

    def update(self, message):
        """Recognize an explicitly mentioned topic."""

        if not isinstance(message, str):
            return self.active_topic

        text = message.casefold().strip()

        # Recognize explicit corrections to the conversation topic.
        correction_patterns = (
            r"^not\s+(?:marcus-01|marcus01|the robot)\.\s*i\s+mean\s+my\s+(car|laptop)\s*[.!?]?$",
            r"^no,?\s*i\s+meant\s+my\s+(car|laptop)\s*[.!?]?$",
            r"^actually,?\s*i(?:['\u2019]m|\s+am)\s+talking\s+about\s+my\s+(car|laptop)\s*[.!?]?$",
        )

        for pattern in correction_patterns:
            match = re.fullmatch(pattern, text)
            if match:
                self.set_topic(match.group(1))
                return self.active_topic

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
            self.set_topic("robot")
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

        # Do not select the robot topic when the user explicitly
        # says they are referring to something else.
        negative_robot_reference = (
            r"^not\s+(?:marcus-01|marcus01|the robot)\b",
            r"^i\s+don['’]t\s+mean\s+(?:marcus-01|marcus01|the robot)\b",
            r"^i\s+do\s+not\s+mean\s+(?:marcus-01|marcus01|the robot)\b",
            r"^i['’]?m\s+not\s+talking\s+about\s+(?:marcus-01|marcus01|the robot)\b",
            r"^i\s+am\s+not\s+talking\s+about\s+(?:marcus-01|marcus01|the robot)\b",
        )

        if any(re.search(pattern, text) for pattern in negative_robot_reference):
            self.clear()
            return self.active_topic

        if any(term in text for term in robot_terms):
            self.set_topic("robot")
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
                self.set_topic(topic)
                return self.active_topic

        return self.active_topic

    def get_topic(self):
        """Return the current conversation topic."""
        return self.active_topic

    def clear(self):
        """Forget the current conversation state."""
        self.active_topic = None
        self.active_subtopic = None
        self.troubleshooting_step = None
        self.diagnostic_details = {}

    def set_topic(self, topic):
        """Change topics and clear outdated conversation state."""
        if topic != self.active_topic:
            self.active_subtopic = None
            self.troubleshooting_step = None
            self.diagnostic_details = {}

        self.active_topic = topic
        return self.active_topic

    def set_subtopic(self, subtopic):
        """Remember the current conversational subtopic."""
        if not isinstance(subtopic, str):
            return False

        subtopic = subtopic.strip()

        if not subtopic:
            return False

        self.active_subtopic = subtopic
        return True

    def get_subtopic(self):
        """Return the current conversational subtopic."""
        return self.active_subtopic

    def clear_subtopic(self):
        """Forget the current conversational subtopic."""
        self.active_subtopic = None

    def set_troubleshooting_step(self, step):
        """Remember the current troubleshooting question."""
        if not isinstance(step, str):
            return False

        step = step.strip()

        if not step:
            return False

        self.troubleshooting_step = step
        return True

    def get_troubleshooting_step(self):
        """Return the current troubleshooting question."""
        return self.troubleshooting_step

    def clear_troubleshooting_step(self):
        """Clear the current troubleshooting question."""
        self.troubleshooting_step = None

    def is_robot_followup(self, message):
        """Detect robot follow-ups using the shared classifier."""

        if self.active_topic != "robot":
            return False

        return classify_robot_question(message) is not None
