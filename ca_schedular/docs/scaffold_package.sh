#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# scaffold_package.sh
# A script to create a Python package layout (no build-tools required).
# -----------------------------------------------------------------------------

set -euo pipefail # enforce stricter error handling

# ─── CONFIG ────────────────────────────────────────────────────────────────────

PKG="alpaca_tradebot"          # Change this to your package name
SRC_DIR="src/${PKG}"
TEST_DIR="tests"

# ─── CREATE DIRECTORIES ────────────────────────────────────────────────────────

echo "Creating directory structure…"
mkdir -p "${SRC_DIR}"
mkdir -p "${TEST_DIR}"

# ─── CREATE __init__.py ───────────────────────────────────────────────────────

cat > "${SRC_DIR}/__init__.py" <<EOF
# ${PKG}
# -----------------------------------------------------------------------------
# Top‑level package for ${PKG}.
#
__version__ = "0.1.0"
EOF

# ─── SAMPLE MODULES ───────────────────────────────────────────────────────────

cat > "${SRC_DIR}/math_utils.py" <<EOF
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
EOF

cat > "${SRC_DIR}/string_utils.py" <<EOF
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
EOF

# ─── TESTS ─────────────────────────────────────────────────────────────────────

cat > "${TEST_DIR}/test_math_utils.py" <<EOF
import unittest
from ${PKG}.math_utils import add

class TestMathUtils(unittest.TestCase):
    def test_add_integers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_floats(self):
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)

if __name__ == "__main__":
    unittest.main()
EOF

cat > "${TEST_DIR}/test_string_utils.py" <<EOF
import unittest
from ${PKG}.string_utils import shout

class TestStringUtils(unittest.TestCase):
    def test_shout(self):
        self.assertEqual(shout("hello"), "HELLO!")

if __name__ == "__main__":
    unittest.main()
EOF

# ─── PROJECT METADATA & OTHER FILES ────────────────────────────────────────────

echo "Creating README, LICENSE, .gitignore…"

cat > README.md <<EOF
# ${PKG}

A minimal Python package scaffolded without build tools.

## Installation

\`\`\`bash
# from project root
pip install .
\`\`\`

## Usage

\`\`\`python
from ${PKG}.math_utils import add
print(add(1, 2))  # 3
\`\`\`
EOF

cat > LICENSE <<EOF
MIT License

Copyright (c) $(date +%Y)

Permission is hereby granted, free of charge, to any person obtaining a copy...
EOF

cat > .gitignore <<EOF
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*\$py.class

# Distribution / packaging
build/
dist/
*.egg-info/

# Virtual env
venv/
EOF

# ─── DONE ──────────────────────────────────────────────────────────────────────

echo "✔ Package '${PKG}' scaffold created!"
