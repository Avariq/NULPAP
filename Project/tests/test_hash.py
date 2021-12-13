from unittest import TestCase
from project.hasher import HashPassword

class TestHash(TestCase):
    def setUp(self):
        self.hasher = HashPassword()

    def test_hashing(self):
        self.assertEqual(self.hasher.Hash("123"), self.hasher.Hash("123"))
        self.assertNotEqual(self.hasher.Hash("123"), self.hasher.Hash("12"))