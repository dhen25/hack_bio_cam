from fastapi import APIRouter, Depends

from coolsense.api.deps import get_orchestrator, require_api_key
from coolsense.api.schemas import ControlOverrideRequest

router = APIRouter(prefix="/v1/controls", tags=["controls"])


@router.post("/override")
def set_override(
    payload: ControlOverrideRequest,
    _: None = Depends(require_api_key),
    orchestrator=Depends(get_orchestrator),
) -> dict:
    return orchestrator.override_controls(payload.model_dump())

