\"\"\"string_utils.py

Provides basic string utility functions.
\"\"\"

def shout(text: str) -> str:
    \"\"\"
    Convert a string to uppercase with an exclamation.

    Args:
        text (str): Input string.

    Returns:
        str: Uppercased string with exclamation.

    Example:
        >>> shout("hello")
        'HELLO!'
    \"\"\"
    return text.upper() + "!"
