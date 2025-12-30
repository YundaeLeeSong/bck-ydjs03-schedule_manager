import unittest
from alpaca_tradebot.math_utils import add

class TestMathUtils(unittest.TestCase):
    def test_add_integers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_floats(self):
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)

if __name__ == "__main__":
    unittest.main()
