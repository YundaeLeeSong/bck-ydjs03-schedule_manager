\"\"\"math_utils.py

Provides basic math utility functions.
\"\"\"

from typing import Union

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    \"\"\"
    Add two numbers.

    Args:
        a (int | float): First operand.
        b (int | float): Second operand.

    Returns:
        int | float: Sum of a and b.

    Example:
        >>> add(2, 3)
        5
    \"\"\"
    return a + b
