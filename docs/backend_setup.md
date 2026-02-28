# Backend Setup (Current Behavior)

## Scope

This describes what the backend currently does in the repo today.

## What Runs

- **API app:** FastAPI app at `coolsense.api.app:app`.
- **Background loop:** starts on API startup and calls orchestrator `tick()` every `COOLSENSE_POLL_INTERVAL_SECONDS` (default `2s`).
- **Data source:** simulator provider (`SimulatorProvider`) is the active source of node readings.
- **State store:** in-memory ring buffer (`history_size` default `500`) stores snapshots.

## Core Flow Per Tick

1. Read all simulator nodes.
2. Compute digital twin state (`compute_system_state`).
3. If model file exists (`coolsense_model.pt` by default), run inference for recommendations.
4. If mode is `auto`, apply recommendations back to the simulator.
5. Save snapshot to history and broadcast over websocket clients.

## API Surface

- `GET /health`  
  Returns service health (`{"status":"ok"}`).

- `GET /v1/state/current`  
  Returns current computed system state.

- `GET /v1/state/history?limit=50&since_ts=...`  
  Returns recent historical snapshots.

- `GET /v1/state/forecast?horizon_hours=6`  
  Returns forecast based on in-memory history.

- `GET /v1/forecast?horizon_hours=6`  
  Alias forecast route.

- `POST /v1/events/inject` *(requires `X-API-Key`)*  
  Injects an event into simulator dynamics.

- `POST /v1/controls/override` *(requires `X-API-Key`)*  
  Overrides controls/mode and applies mapped recommendations.

- `POST /v1/model/train` *(requires `X-API-Key`)*  
  Stub endpoint; currently returns `NOT_IMPLEMENTED`.

- `GET /v1/model/status`  
  Returns model loaded status and effective mode.

- `GET /metrics`  
  Prometheus-style metrics output.

- `WS /v1/stream`  
  Streams latest snapshots every ~2 seconds.  
  Optional auth via query param `api_key` when `COOLSENSE_READ_REQUIRES_AUTH=true`.

## Security + Guardrails

- Mutating endpoints use API key dependency (`X-API-Key`).
- Request middleware adds/propagates `X-Request-Id`.
- Per-IP+path in-memory rate limiting:
  - reads: `COOLSENSE_READ_RATE_LIMIT_PER_MINUTE` (default `120`)
  - mutating: `COOLSENSE_MUTATING_RATE_LIMIT_PER_MINUTE` (default `30`)

## Runtime Mode

- `COOLSENSE_MODE=auto` (default): apply model recommendations to simulator.
- `COOLSENSE_MODE=manual`: recommendations can be computed but not auto-applied.

## What Is Not Implemented Yet

- Model training API endpoint behavior (`/v1/model/train`) is placeholder only.
- Persistence beyond process lifetime is not wired into these state endpoints (history is in-memory ring buffer).

## Run and Verify

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,db,ml,ui]"
export COOLSENSE_API_KEY=dev-key
uvicorn coolsense.api.app:app --reload
```

In another terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/state/current
curl "http://localhost:8000/v1/state/forecast?horizon_hours=6"
curl -X POST "http://localhost:8000/v1/events/inject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{"type":"rain_spike","magnitude":0.3}'
```

## Demo Automation

Preflight:

```bash
. .venv/bin/activate
export COOLSENSE_API_KEY=dev-key
python scripts/verify_demo.py
```

One-command run:

```bash
. .venv/bin/activate
./scripts/demo_run.sh --retrain
```

This starts API + dashboard, injects a deterministic contamination sequence, and leaves both services running.
