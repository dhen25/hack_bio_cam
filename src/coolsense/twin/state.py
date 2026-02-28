from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from coolsense.api.schemas import (
    BiocideBlock,
    CorrosionBlock,
    DischargeBlock,
    Exceedance,
    NodeReading,
    SensorReadings,
    SystemState,
)
from coolsense.config.defaults import DEFAULT_MAKEUP_CHEMISTRY, DEFAULT_PERMIT_LIMITS
from coolsense.twin.biocide import biocide_model
from coolsense.twin.blowdown import blowdown_predictor
from coolsense.twin.concentration import concentration_model
from coolsense.twin.corrosion import corrosion_model
from coolsense.twin.phosphorus import phosphorus_estimate


def compute_system_state(
    nodes: dict[str, Any],
    settings: dict[str, Any] | None = None,
    recent_history: list[dict[str, Any]] | None = None,
) -> SystemState:
    _ = recent_history
    settings = settings or {}
    makeup = settings.get("makeup_chemistry", DEFAULT_MAKEUP_CHEMISTRY)
    permit = settings.get("permit_limits", DEFAULT_PERMIT_LIMITS)
    blowdown_m3_day = float(settings.get("blowdown_rate_m3_day", 50.0))

    node1 = nodes["node1"]
    node2 = nodes["node2"]
    node3 = nodes["node3"]
    node4 = nodes["node4"]

    internal = nodes.get("_internal", {})
    coc, basin = concentration_model(node1_ec=node1["ec"], node2_ec=node2["ec"], makeup=makeup)
    ambient_temp_c = float(internal.get("ambient_temp_c", 35.0))
    corrosion = corrosion_model(
        node2_ph=node2["ph"],
        node3_ph=node3["ph"],
        node2_ec=node2["ec"],
        node3_ec=node3["ec"],
        node2_turbidity=node2["turbidity"],
        node3_turbidity=node3["turbidity"],
        ambient_temp_c=ambient_temp_c,
    )
    biocide = biocide_model(
        biocide_dose_mgL=float(internal.get("true_biocide_residual", 1.0)),
        hours_since_dose=0.0,
        ph=node2["ph"],
    )
    phosphorus = phosphorus_estimate(coc, makeup["inhibitor_phosphorus_mgL"])
    compliance = blowdown_predictor(
        node4=node4,
        basin=basin,
        corrosion=corrosion,
        biocide=biocide,
        phosphorus_mgL=phosphorus,
        permit_limits=permit,
        blowdown_m3_day=blowdown_m3_day,
    )

    ts_raw = nodes.get("timestamp")
    ts = datetime.fromisoformat(ts_raw) if isinstance(ts_raw, str) else datetime.now(timezone.utc)

    return SystemState(
        nodes=SensorReadings(
            node1=NodeReading(**node1),
            node2=NodeReading(**node2),
            node3=NodeReading(**node3),
            node4=NodeReading(**node4),
            timestamp=ts,
        ),
        coc=coc,
        basin_chemistry={**basin, "phosphorus_mgL": phosphorus},
        corrosion=CorrosionBlock(
            cu_ppb=float(corrosion["cu_ppb"]),
            zn_ppb=float(corrosion["zn_ppb"]),
            severity_index=float(corrosion["severity_index"]),
            source_diagnosis=str(corrosion["source_diagnosis"]),
        ),
        biocide=BiocideBlock(
            total_chlorine_mgL=float(biocide["total_chlorine_mgL"]),
            effective_hocl_mgL=float(biocide["effective_hocl_mgL"]),
            hocl_fraction_pct=float(biocide["hocl_fraction_pct"]),
            status=str(biocide["status"]),
        ),
        discharge=DischargeBlock(
            predicted_next_1h=compliance["discharge_composition"],
            mass_loadings_per_day=compliance["mass_loadings_per_day"],
        ),
        exceedances=[Exceedance(**exc) for exc in compliance["exceedances"]],
        compliant=bool(compliance["compliant"]),
        timestamp=ts,
    )
