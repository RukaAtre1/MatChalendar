#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

if [[ ! -f "backend/main.py" ]]; then
  echo "backend/main.py was not found. Run this script from the MatChalendar project."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if [[ -f "requirements.txt" ]]; then
  python -m pip install -r requirements.txt
fi

export MATCHALENDAR_HOST="${MATCHALENDAR_HOST:-0.0.0.0}"
export MATCHALENDAR_PORT="${MATCHALENDAR_PORT:-8000}"

echo "Starting MatChalendar backend from ${PROJECT_ROOT}"
echo "Local health:  http://127.0.0.1:${MATCHALENDAR_PORT}/api/health"
echo "LAN address:   http://<gx10-ip>:${MATCHALENDAR_PORT}"
echo ""

python backend/main.py
