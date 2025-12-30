"""
geometry module
===============

Provides simple geometric calculations.
"""

import math


def circle_area(radius):
    """
    Compute the area of a circle.

    :param radius: Radius of the circle.
    :type radius: float
    :return: Area of the circle.
    :rtype: float

    Examples:
        >>> from mathutils.geometry import circle_area
        >>> round(circle_area(1), 5)
        3.14159

    CLI Test:
        $ python -c "from mathutils.geometry import circle_area; print(circle_area(2.5))"
    """
    return math.pi * radius ** 2


def rectangle_perimeter(width, height):
    """
    Compute the perimeter of a rectangle.

    :param width: Width of the rectangle.
    :type width: float
    :param height: Height of the rectangle.
    :type height: float
    :return: Perimeter (2*(width + height)).
    :rtype: float

    Examples:
        >>> from mathutils.geometry import rectangle_perimeter
        >>> rectangle_perimeter(3, 4)
        14.0

    CLI Test:
        $ python -c "from mathutils.geometry import rectangle_perimeter; \
print(rectangle_perimeter(5, 7))"
    """
    return 2 * (width + height)
