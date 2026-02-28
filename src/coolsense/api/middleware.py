from __future__ import annotations

import time
from collections import defaultdict, deque
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from coolsense.api.errors import build_error
from coolsense.config.settings import get_settings
from coolsense.observability.logging import log_request
from coolsense.observability.metrics import get_metrics

_RATE_BUCKETS: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def _is_mutating(method: str) -> bool:
    return method.upper() in {"POST", "PUT", "PATCH", "DELETE"}


def reset_rate_limits() -> None:
    _RATE_BUCKETS.clear()


async def request_context_and_rate_limit(request: Request, call_next):
    started = time.time()
    trace_id = request.headers.get("X-Request-Id", str(uuid4()))
    request.state.trace_id = trace_id

    settings = getattr(request.app.state, "settings", get_settings())
    read_limit = int(settings.get("read_rate_limit_per_minute", 120))
    mutating_limit = int(settings.get("mutating_rate_limit_per_minute", 30))
    limit = mutating_limit if _is_mutating(request.method) else read_limit

    ip = request.client.host if request.client else "unknown"
    key = (ip, request.url.path)
    now = time.time()
    q = _RATE_BUCKETS[key]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        get_metrics().errors_total += 1
        return JSONResponse(
            status_code=429,
            content=build_error(
                "RATE_LIMITED",
                "Too many requests",
                trace_id,
                {"limit_per_minute": limit},
            ),
            headers={"X-Request-Id": trace_id},
        )
    q.append(now)

    response = await call_next(request)
    response.headers["X-Request-Id"] = trace_id

    duration_ms = (time.time() - started) * 1000.0
    metrics = get_metrics()
    metrics.requests_total += 1
    if response.status_code >= 400:
        metrics.errors_total += 1
    log_request(trace_id, request.method, request.url.path, response.status_code, duration_ms)
    return response
