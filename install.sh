#!/usr/bin/env bash
# Provisions the local development environment for the Hebrew Language Tutor.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON_BIN="${PYTHON_BIN:-python3.13}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: $PYTHON_BIN not found. Install Python 3.13 or set PYTHON_BIN to a compatible interpreter." >&2
  exit 1
fi

"$PYTHON_BIN" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p tmp
touch tmp/.gitkeep

echo "Environment ready. Activate with 'source .venv/bin/activate' or run './run.sh'."
