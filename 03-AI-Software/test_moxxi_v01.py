
"""MOXXI v0.1 baseline regression tests."""

import unittest

from conversation import respond, respond_with_knowledge
from history import search_conversations
from knowledge import find_robot_fact


class TestMoxxiV01(unittest.TestCase):

    def setUp(self):
        self.memory = {"user_name": "David", "conversations": 0}

    def test_robot_identity(self):
        self.assertEqual(
            find_robot_fact("robot", "project_name"),
            "MARCUS-01"
        )

    def test_ai_identity(self):
        self.assertEqual(
            find_robot_fact("robot", "ai_name"),
            "MOXXI"
        )

    def test_robot_height(self):
        self.assertEqual(
            find_robot_fact("robot", "target_height_inches"),
            42
        )

    def test_drive_configuration(self):
        self.assertEqual(
            find_robot_fact("hardware", "drive_configuration"),
            "Two powered side wheels"
        )

    def test_knowledge_response(self):
        response = respond(
            "How tall is MARCUS-01?", self.memory
        )
        self.assertIn("42 inches", response)

    def test_name_memory(self):
        response = respond(
            "What is my name?", self.memory
        )
        self.assertIn("David", response)

    def test_greeting(self):
        response = respond("hello", self.memory)
        self.assertIsInstance(response, str)
        self.assertTrue(response.strip())

    def test_unknown_knowledge_question(self):
        self.assertIsNone(
            respond_with_knowledge("What is the weather?")
        )

    def test_invalid_knowledge_input(self):
        self.assertIsNone(
            respond_with_knowledge(None)
        )

    def test_history_search(self):
        results = search_conversations(
            "robot", mode="user"
        )
        self.assertIsInstance(results, list)

    def test_voice_status(self):
        self.assertEqual(
            find_robot_fact("software", "voice_interface"),
            "Planned"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
