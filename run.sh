#!/usr/bin/env bash
# Starts the Hebrew Language Tutor app: a single FastAPI process serving both
# the JSON API and the static frontend (Bootstrap via CDN, no build step).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
  echo "error: .venv not found. Run ./install.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Entry point convention: backend/main.py exposing an `app` FastAPI instance,
# imported as `backend.main:app`. If Stage 6 lays out the backend module
# differently, update this import target accordingly (see environment-notes.md).
exec uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload
