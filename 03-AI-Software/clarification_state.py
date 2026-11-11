"""Track a question waiting for clarification."""


class ClarificationState:
    """Store one unresolved question during a conversation."""

    def __init__(self):
        self.pending_question = None

    def set_pending(self, question):
        """Remember the question that needs clarification."""
        if not isinstance(question, str):
            return False

        question = question.strip()

        if not question:
            return False

        self.pending_question = question
        return True

    def get_pending(self):
        """Return the unresolved question, if any."""
        return self.pending_question

    def has_pending(self):
        """Check whether clarification is needed."""
        return self.pending_question is not None

    def clear(self):
        """Forget the unresolved question."""
        self.pending_question = None

    def resolve(self, answer):
        """Return the original question when MARCUS-01 is confirmed."""
        if not self.has_pending():
            return None

        if not isinstance(answer, str):
            return None

        text = answer.casefold().strip().rstrip("?.!")

        confirmations = (
            "marcus-01",
            "marcus01",
            "the robot",
            "your robot",
            "i meant marcus-01",
            "i meant marcus01",
            "i meant the robot",
            "i'm talking about the robot",
            "im talking about the robot",
            "i am talking about the robot",
            "i'm talking about marcus-01",
            "im talking about marcus-01",
            "yes, marcus-01",
            "yes marcus-01",
            "yes, the robot",
            "yes the robot",
            "i mean marcus-01",
            "i mean the robot",
        )

        if text in confirmations:
            question = self.pending_question
            self.clear()
            return question

        return None
