import random

RESPONSES = {
    "greetings": [
        "Well, hello there, sugar! Ready to cause a little mechanical mischief?",
        "Look who showed up! MOXXI is at your service, darling.",
        "Hey, sugar! Your favorite robotic troublemaker is online.",
    ],
    "moods": [
        "All systems looking fabulous, darling!",
        "Feeling positively electric, sugar!",
        "My circuits are humming and my attitude is excellent!",
    ],
    "fallbacks": [
        "Interesting, darling. Tell me a little more.",
        "You've got my attention, sugar. What are we working on?",
        "Now that's intriguing! Care to elaborate?",
    ],
}

def get_response(category):
    options = RESPONSES.get(category)
    if not options:
        return None
    return random.choice(options)


if __name__ == "__main__":
    print("STEP 534: RESPONSE LIBRARY TEST")
    for category in ("greetings", "moods", "fallbacks"):
        result = get_response(category)
        print(f"{category.upper()}: {result}")
        assert result in RESPONSES[category]
    print("STEP 534 TEST PASSED")
