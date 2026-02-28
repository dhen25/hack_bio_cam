# CoolSense

Backend-first cooling tower simulation and optimization system.

## Local Development

### 1) Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,db,ml,ui]"
```

### 2) Run API locally

```bash
export COOLSENSE_API_KEY=dev-key
uvicorn coolsense.api.app:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

Export contracts:

```bash
python scripts/export_openapi.py
```

### 3) Run tests

```bash
pytest -q
python -m compileall src
```

## Docker Compose

```bash
docker compose up --build
```

The API container starts FastAPI on port `8000` and Postgres on `5432`.

Mutating endpoints (event injection, controls override, model train) require `X-API-Key`.

## Project Layout (initial)

- `src/coolsense/`: application package.
- `scripts/`: helper scripts (OpenAPI export, seed data, etc.).
- `tests/`: automated tests.

## Placeholders for later cycles

- Simulator/provider abstraction
- Digital twin models
- Neural network optimizer
- Orchestrator loop + streaming
- Dashboard application

## Simulator smoke loop

```bash
. .venv/bin/activate
python -c "from coolsense.simulator.simulator import CoolingTowerSimulator as S; s=S(); print(s.read_all_nodes().keys())"
pytest -q tests/test_simulator.py
```

## Twin smoke test

```bash
. .venv/bin/activate
pytest -q tests/test_twin.py tests/test_forecast.py
python -c "from coolsense.simulator.simulator import CoolingTowerSimulator as S; from coolsense.twin.state import compute_system_state; s=S(); print(compute_system_state(s.read_all_nodes()).model_dump().keys())"
```

## Train optimizer

```bash
. .venv/bin/activate
python train.py
test -f coolsense_model.pt
pytest -q tests/test_optimizer.py tests/test_score.py
```

## Run orchestrator (terminal mode)

```bash
. .venv/bin/activate
python main.py
```

## Run API with live loop

```bash
. .venv/bin/activate
uvicorn coolsense.api.app:app --reload
curl http://localhost:8000/v1/state/current
curl http://localhost:8000/v1/forecast?horizon_hours=6
```

## Observability and security hardening

- Structured request logs include `trace_id`, method, path, status, duration.
- Request IDs are accepted via `X-Request-Id` and returned on responses.
- Basic per-path rate limiting is enabled in middleware.
- Prometheus-style metrics are available at `/metrics`.

```bash
. .venv/bin/activate
curl http://localhost:8000/metrics
```

## Quality and CI

```bash
. .venv/bin/activate
ruff check src tests
black --check src tests
pytest -q
python scripts/export_openapi.py
git diff -- contracts/openapi.json
```

Demo script: `docs/demo_flow.md`.

## Dashboard

```bash
. .venv/bin/activate
streamlit run apps/dashboard/app.py
```

Environment:
- `COOLSENSE_API_BASE_URL` defaults to `http://localhost:8000`
- `COOLSENSE_API_KEY` is used for protected event controls
