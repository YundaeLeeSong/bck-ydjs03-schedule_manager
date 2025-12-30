"""
arithmetic module
=================

Provides basic arithmetic operations.
"""

def add(a, b):
    """
    Add two numbers.

    :param a: First addend.
    :type a: int or float
    :param b: Second addend.
    :type b: int or float
    :return: Sum of a and b.
    :rtype: int or float

    Examples:
        >>> from mathutils.arithmetic import add
        >>> add(2, 3)
        5

    CLI Test:
        $ python -c "from mathutils.arithmetic import add; print(add(10, 20))"
    """
    return a + b


def multiply(a, b):
    """
    Multiply two numbers.

    :param a: First factor.
    :type a: int or float
    :param b: Second factor.
    :type b: int or float
    :return: Product of a and b.
    :rtype: int or float

    Examples:
        >>> from mathutils.arithmetic import multiply
        >>> multiply(4, 5)
        20

    CLI Test:
        $ python -c "from mathutils.arithmetic import multiply; print(multiply(7, 6))"
    """
    return a * b
