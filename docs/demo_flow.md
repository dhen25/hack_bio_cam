# CoolSense Demo Flow

## Preflight

```bash
. .venv/bin/activate
export COOLSENSE_API_KEY=dev-key
python scripts/verify_demo.py
```

## One-command demo

```bash
. .venv/bin/activate
./scripts/demo_run.sh --retrain
```

## Manual scripted sequence

1. Start API and dashboard.
2. Verify baseline:
   - `GET /v1/state/current`
   - `GET /v1/model/status`
3. Inject concentration stress:
   - `POST /v1/events/inject` with `{"type":"concentration_buildup","magnitude":1.4}`
4. Inject segment corrosion:
   - `POST /v1/events/inject` with `{"type":"corrosion_spike","magnitude":1.6}`
5. Inject pH depression:
   - `POST /v1/events/inject` with `{"type":"ph_drop","magnitude":1.2}`
6. Confirm expected behavior:
   - Node deltas indicate where contamination is introduced.
   - Estimated Cu/Zn and compliance risk rise in twin outputs.
   - Recommendations adjust blowdown, biocide dose, pH setpoint, and CoC target.
   - Forecast panel shows forward risk trajectory.

## Verification endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/state/current
curl "http://localhost:8000/v1/forecast?horizon_hours=6"
curl http://localhost:8000/v1/model/status
```
