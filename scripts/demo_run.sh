#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
fi

: "${COOLSENSE_API_KEY:=dev-key}"
export COOLSENSE_API_KEY
export COOLSENSE_API_BASE_URL="${COOLSENSE_API_BASE_URL:-http://localhost:8000}"

python "scripts/verify_demo.py"

if [[ "${1:-}" == "--retrain" ]]; then
  python "train.py"
fi

uvicorn coolsense.api.app:app --host 0.0.0.0 --port 8000 > /tmp/coolsense_api.log 2>&1 &
API_PID=$!

cleanup() {
  kill "$API_PID" >/dev/null 2>&1 || true
  kill "$DASH_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in {1..30}; do
  if curl -sSf "http://localhost:8000/health" >/dev/null; then
    break
  fi
  sleep 1
done

streamlit run "apps/dashboard/app.py" --server.port 8501 > /tmp/coolsense_dashboard.log 2>&1 &
DASH_PID=$!

sleep 2

curl -sS -X POST "http://localhost:8000/v1/events/inject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${COOLSENSE_API_KEY}" \
  -d '{"type":"concentration_buildup","magnitude":1.4}' >/dev/null
sleep 3
curl -sS -X POST "http://localhost:8000/v1/events/inject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${COOLSENSE_API_KEY}" \
  -d '{"type":"corrosion_spike","magnitude":1.6}' >/dev/null
sleep 3
curl -sS -X POST "http://localhost:8000/v1/events/inject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${COOLSENSE_API_KEY}" \
  -d '{"type":"ph_drop","magnitude":1.2}' >/dev/null

echo "Demo is running:"
echo "- API: http://localhost:8000"
echo "- Dashboard: http://localhost:8501"
echo "- API logs: /tmp/coolsense_api.log"
echo "- Dashboard logs: /tmp/coolsense_dashboard.log"
echo "Press Ctrl+C to stop."

wait "$API_PID" "$DASH_PID"
