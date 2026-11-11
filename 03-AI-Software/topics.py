
import re

TOPIC_GROUPS = {
    "robot": {"robot", "robots", "robotic", "robotics", "marcus-01", "marcus01"},
    "wheels": {"wheel", "wheels", "drivetrain"},
    "touchscreen": {"touchscreen", "touchscreens", "touch screen", "display", "screen"},
    "memory": {"memory", "memories", "remember", "remembering", "recall"},
}


def topic_matches(query, text):
    query = str(query).casefold().strip()
    text = str(text).casefold()

    if not query or not text:
        return False

    def contains(term):
        return re.search(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            text
        ) is not None

    if contains(query):
        return True

    for terms in TOPIC_GROUPS.values():
        if query in terms:
            return any(contains(term) for term in terms)

    return False


if __name__ == "__main__":
    tests = [
        ("robots", "I built a robot", True),
        ("robot", "MARCUS-01 is my project", True),
        ("wheel", "MOXXI needs wheels", True),
        ("screen", "Install a touchscreen", True),
        ("memory", "MOXXI should remember", True),
        ("robot", "I like painting", False),
    ]

    for query, message, expected in tests:
        result = topic_matches(query, message)
        print(f"{query}: {result}")
        assert result == expected

    print("ALL TOPIC TESTS PASSED: True")
