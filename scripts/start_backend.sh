#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

if [ ! -f "backend/main.py" ]; then
    echo "backend/main.py was not found. Run this script from the MatChalendar project, or check that scripts/start_backend.sh is inside the project root." >&2
    exit 1
fi

if [ -f ".env.local" ]; then
    echo "Found .env.local; backend/config.py will load it."
fi

echo "Starting MatChalendar backend from $PROJECT_ROOT"
echo "Health:         http://127.0.0.1:8000/api/health"
echo "Runtime status: http://127.0.0.1:8000/api/runtime/status"
echo "Agentverse:     http://127.0.0.1:8000/api/agentverse/plan"
echo

python backend/main.py
