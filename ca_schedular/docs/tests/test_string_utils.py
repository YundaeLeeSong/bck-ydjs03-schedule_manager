import unittest
from alpaca_tradebot.string_utils import shout

class TestStringUtils(unittest.TestCase):
    def test_shout(self):
        self.assertEqual(shout("hello"), "HELLO!")

if __name__ == "__main__":
    unittest.main()
