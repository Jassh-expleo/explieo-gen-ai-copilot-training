#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "──────────────────────────────────────────"
echo "  Explieo Agent Orchestrator Monitor"
echo "──────────────────────────────────────────"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Please install Python 3.10+."
  exit 1
fi

# Install deps if needed
if ! python3 -c "import fastapi, uvicorn, watchdog" 2>/dev/null; then
  echo "Installing dependencies…"
  pip3 install -r requirements.txt -q
fi

echo "Starting server at http://localhost:8765"
echo "Watching: ../.github/agent-workflow/runs/"
echo "Press Ctrl+C to stop."
echo ""
python3 server.py
