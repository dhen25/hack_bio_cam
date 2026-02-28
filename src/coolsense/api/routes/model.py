from fastapi import APIRouter, Depends

from coolsense.api.deps import get_orchestrator, require_api_key
from coolsense.api.schemas import ModelStatusResponse, TrainResponse

router = APIRouter(prefix="/v1/model", tags=["model"])


@router.post("/train", response_model=TrainResponse)
def train_model(_: None = Depends(require_api_key)) -> TrainResponse:
    return TrainResponse(accepted=False, message="NOT_IMPLEMENTED")


@router.get("/status", response_model=ModelStatusResponse)
def model_status(orchestrator=Depends(get_orchestrator)) -> ModelStatusResponse:
    mode = "auto" if orchestrator.mode == "auto" else "manual"
    return ModelStatusResponse(model_loaded=orchestrator.model_loaded, mode=mode)
