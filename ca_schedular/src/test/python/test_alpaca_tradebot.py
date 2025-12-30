import unittest
from mathutils.arithmetic import add, multiply
from mathutils.geometry import circle_area, rectangle_perimeter
import math

class TestArithmetic(unittest.TestCase):

    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertAlmostEqual(add(2.5, 0.5), 3.0)

    def test_multiply(self):
        self.assertEqual(multiply(4, 5), 20)
        self.assertAlmostEqual(multiply(2.5, 2), 5.0)

class TestGeometry(unittest.TestCase):

    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(1), math.pi)
        self.assertAlmostEqual(circle_area(2.5), math.pi * 2.5**2)

    def test_rectangle_perimeter(self):
        self.assertEqual(rectangle_perimeter(3, 4), 14.0)
        self.assertEqual(rectangle_perimeter(5.5, 2.2), 2 * (5.5 + 2.2))




if __name__ == "__main__":
    unittest.main()
