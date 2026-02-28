from fastapi import APIRouter, Depends, Query

from coolsense.api.deps import get_orchestrator, require_api_key
from coolsense.api.schemas import ModelStatusResponse, TrainResponse

router = APIRouter(prefix="/v1/model", tags=["model"])


@router.post("/train", response_model=TrainResponse)
def train_model(
    n_scenarios: int = Query(default=500, ge=50, le=5000),
    seed: int = Query(default=42, ge=0, le=999999),
    _: None = Depends(require_api_key),
    orchestrator=Depends(get_orchestrator),
) -> TrainResponse:
    artifact = orchestrator.train_model(n_scenarios=n_scenarios, seed=seed)
    sample_count = int(artifact.get("sample_count", 0))
    return TrainResponse(accepted=True, message=f"TRAINED sample_count={sample_count}")


@router.get("/status", response_model=ModelStatusResponse)
def model_status(orchestrator=Depends(get_orchestrator)) -> ModelStatusResponse:
    mode = "auto" if orchestrator.mode == "auto" else "manual"
    return ModelStatusResponse(model_loaded=orchestrator.model_loaded, mode=mode)
