# CoolSense Demo Flow

1. Start backend loop and API.
2. Verify baseline compliance and recommendations.
3. Inject `corrosion_spike` via `POST /v1/events/inject`.
4. Observe rise in node3 turbidity and corrosion estimates, then recommendation changes.
5. Inject `biocide_overdose` and verify elevated chlorine plus dose-reduction recommendation.
6. Inject `makeup_quality_drop` and verify multi-parameter degradation and adaptive control.
7. Confirm trend back toward compliance in `/v1/state/current` and `/v1/state/history`.
