from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeReading(BaseModel):
    ph: float = Field(ge=0.0, le=14.0)
    ec: float = Field(ge=0.0)
    turbidity: float = Field(ge=0.0)


class SensorReadings(BaseModel):
    node1: NodeReading
    node2: NodeReading
    node3: NodeReading
    node4: NodeReading
    timestamp: datetime


class CorrosionBlock(BaseModel):
    cu_ppb: float = 0.0
    zn_ppb: float = 0.0
    severity_index: float = 0.0
    source_diagnosis: str = "unknown"


class BiocideBlock(BaseModel):
    total_chlorine_mgL: float = 0.0
    effective_hocl_mgL: float = 0.0
    hocl_fraction_pct: float = 0.0
    status: str = "unknown"


class DischargeBlock(BaseModel):
    predicted_next_1h: dict[str, float] = Field(default_factory=dict)
    mass_loadings_per_day: dict[str, float] = Field(default_factory=dict)


class Exceedance(BaseModel):
    parameter: str
    measured: float
    limit: float
    severity: float


class SystemState(BaseModel):
    nodes: SensorReadings
    coc: float = 1.0
    basin_chemistry: dict[str, float] = Field(default_factory=dict)
    corrosion: CorrosionBlock = Field(default_factory=CorrosionBlock)
    biocide: BiocideBlock = Field(default_factory=BiocideBlock)
    discharge: DischargeBlock = Field(default_factory=DischargeBlock)
    exceedances: list[Exceedance] = Field(default_factory=list)
    compliant: bool = True
    timestamp: datetime


class Recommendation(BaseModel):
    recommended_blowdown_rate_m3_day: float
    recommended_biocide_dose_mgL: float
    recommended_ph_setpoint: float
    recommended_coc_target: float
    reasoning: list[str] = Field(default_factory=list)


class EventType(str, Enum):
    corrosion_spike = "corrosion_spike"
    biocide_overdose = "biocide_overdose"
    biocide_underdose = "biocide_underdose"
    makeup_quality_drop = "makeup_quality_drop"
    concentration_buildup = "concentration_buildup"
    ph_drop = "ph_drop"
    turbidity_event = "turbidity_event"


class EventInjectionRequest(BaseModel):
    type: EventType
    magnitude: float = Field(gt=0.0, default=1.0)


class OverrideMode(str, Enum):
    auto = "auto"
    manual = "manual"


class ControlOverrideRequest(BaseModel):
    mode: OverrideMode = OverrideMode.manual
    blowdown_rate_m3_day: float | None = Field(default=None, gt=0.0)
    biocide_dose_mgL: float | None = Field(default=None, gt=0.0)
    ph_setpoint: float | None = Field(default=None, ge=6.5, le=9.5)
    coc_target: float | None = Field(default=None, ge=1.0, le=10.0)


class HistoryPoint(BaseModel):
    timestamp: datetime
    coc: float
    cu_ppb: float
    zn_ppb: float
    chlorine_mgL: float
    turbidity_node4: float
    ph_node4: float
    compliant: bool
    recommendation: Recommendation | None = None


class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_cu_ppb: float
    predicted_zn_ppb: float
    predicted_chlorine_mgL: float
    predicted_turbidity_node4: float
    compliant: bool


class ForecastResponse(BaseModel):
    horizon_hours: int = Field(ge=1, le=24)
    points: list[ForecastPoint] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    trace_id: str


class ModelStatusResponse(BaseModel):
    model_loaded: bool
    mode: str


class TrainResponse(BaseModel):
    accepted: bool
    message: str
