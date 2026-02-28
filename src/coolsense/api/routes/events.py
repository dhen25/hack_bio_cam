from fastapi import APIRouter, Depends

from coolsense.api.deps import get_orchestrator, require_api_key
from coolsense.api.schemas import EventInjectionRequest

router = APIRouter(prefix="/v1/events", tags=["events"])


@router.post("/inject")
def inject_event(
    payload: EventInjectionRequest,
    _: None = Depends(require_api_key),
    orchestrator=Depends(get_orchestrator),
) -> dict:
    return orchestrator.inject_event(payload.type.value, payload.magnitude)

