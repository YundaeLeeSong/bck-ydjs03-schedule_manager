#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# temp.sh
# A script to create a Python package layout (no build-tools required).
# -----------------------------------------------------------------------------

set -euo pipefail # enforce stricter error handling







# ─── CONFIG ────────────────────────────────────────────────────────────────────

PKG="alpaca_tradebot"          # Change this to your package name
SRC_DIR="src/${PKG}"
TEST_DIR="tests"




# ─── DONE ──────────────────────────────────────────────────────────────────────

echo "✔ Package '${PKG}' scaffold created!"
echo "(1)      source ../venv/Scripts/activate"
echo "(2)      python dev.py"
echo "(3)      python cli.py"