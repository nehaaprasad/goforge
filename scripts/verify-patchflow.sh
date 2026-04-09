#!/usr/bin/env bash
# Run from repository root: bash scripts/verify-patchflow.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/backend/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Expected backend venv at backend/.venv — create it and pip install -r backend/requirements.txt" >&2
  exit 1
fi

echo "== Backend unit tests =="
cd "$ROOT/backend"
"$PY" -m unittest discover -s tests -v

echo "== In-process API smoke =="
"$PY" scripts/smoke_api.py

echo "== Frontend production build =="
cd "$ROOT/frontend"
npm run build

echo "== docker compose config =="
cd "$ROOT"
if command -v docker >/dev/null 2>&1; then
  docker compose config -q && echo "docker compose: OK"
else
  echo "docker: not installed, skipping compose check"
fi

echo ""
echo "All verification steps passed."
