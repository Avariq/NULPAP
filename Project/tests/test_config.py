from unittest import TestCase;
from project.config import DB_URI;

class TestConfig(TestCase):
    def test_db_uri_exist(self):
        self.assertIsNotNone(DB_URI)