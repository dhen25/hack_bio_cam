from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from coolsense.config.defaults import DEFAULT_PERMIT_LIMITS

try:
    from apps.dashboard.client import CoolSenseClient
except ModuleNotFoundError:
    from client import CoolSenseClient


st.set_page_config(page_title="CoolSense Dashboard", layout="wide")
st_autorefresh(interval=2000, key="coolsense_refresh")
client = CoolSenseClient()

st.title("CoolSense Dashboard")

with st.sidebar:
    st.header("Demo Controls")
    try:
        model_status = client.model_status()
        st.caption(
            f"Model loaded: {'yes' if model_status.get('model_loaded') else 'no'} | mode: {model_status.get('mode')}"
        )
    except Exception:
        st.caption("Model status unavailable")

    if st.button("Train / Refresh Model", use_container_width=True):
        try:
            result = client.train_model(n_scenarios=300, seed=42)
            st.success(result.get("message", "Model trained"))
        except Exception as exc:  # pragma: no cover
            st.error(f"Train failed: {exc}")

    st.divider()
    st.subheader("Event Injection")
    for event_name in [
        "corrosion_spike",
        "biocide_overdose",
        "biocide_underdose",
        "makeup_quality_drop",
        "concentration_buildup",
        "ph_drop",
        "turbidity_event",
    ]:
        if st.button(event_name.replace("_", " ").title(), use_container_width=True):
            try:
                client.inject_event(event_name, 1.5)
                st.success(f"Injected {event_name}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Inject failed: {exc}")

snapshot = client.ws_snapshot()
if snapshot and "state" in snapshot:
    state = snapshot["state"]
else:
    try:
        state = client.current_state()
    except Exception as exc:  # pragma: no cover
        st.error(f"Backend unreachable: {exc}")
        st.stop()

history = client.history(limit=120)
forecast = client.forecast(horizon_hours=6)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Panel 1 - Live Sensor Data")
    node1 = state["nodes"]["node1"]
    for node_name in ("node1", "node2", "node3", "node4"):
        node = state["nodes"][node_name]
        color = "🟢"
        if node["turbidity"] > DEFAULT_PERMIT_LIMITS["turbidity_ntu"] * 0.6:
            color = "🟡"
        if node["turbidity"] > DEFAULT_PERMIT_LIMITS["turbidity_ntu"]:
            color = "🔴"
        st.metric(
            label=f"{color} {node_name.upper()}",
            value=f"pH {node['ph']:.2f} | EC {node['ec']:.0f} | Turb {node['turbidity']:.1f}",
            delta=f"ΔEC vs node1: {node['ec'] - node1['ec']:.0f}, ΔTurb vs node1: {node['turbidity'] - node1['turbidity']:.1f}",
        )

with col2:
    st.subheader("Panel 2 - Digital Twin")
    st.write(f"CoC: {state['coc']:.2f} (target operating band ~3-8)")
    st.write(
        f"Inferred Cu/Zn: {state['corrosion']['cu_ppb']:.1f} / {state['corrosion']['zn_ppb']:.1f} ppb | "
        f"Corrosion severity: {state['corrosion']['severity_index']:.2f}"
    )
    st.write(
        f"Biocide total/effective: {state['biocide']['total_chlorine_mgL']:.2f} / "
        f"{state['biocide']['effective_hocl_mgL']:.2f} mg/L"
    )
    discharge = state.get("discharge", {}).get("predicted_next_1h", {})
    st.write(
        f"Blowdown risk (next 1h): Cu {discharge.get('cu_ppb', 0.0):.1f} ppb, "
        f"Zn {discharge.get('zn_ppb', 0.0):.1f} ppb, TRC {discharge.get('trc_mgL', 0.0):.2f} mg/L"
    )
    st.write(f"Compliance now: {'YES' if state['compliant'] else 'NO'}")
    if state["exceedances"]:
        st.error("Exceedances: " + ", ".join(exc["parameter"] for exc in state["exceedances"]))
    else:
        st.success("All monitored limits within configured thresholds")

col3, col4 = st.columns(2)
with col3:
    st.subheader("Panel 3 - Trend Charts")
    times = [datetime.fromisoformat(p["timestamp"]) for p in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[p["cu_ppb"] for p in history], name="Cu ppb"))
    fig.add_trace(go.Scatter(x=times, y=[p["chlorine_mgL"] for p in history], name="Chlorine mg/L"))
    fig.add_trace(go.Scatter(x=times, y=[p["coc"] for p in history], name="CoC"))
    fig.add_trace(go.Scatter(x=times, y=[p["turbidity_node4"] for p in history], name="Turbidity node4"))
    fig.add_hline(y=DEFAULT_PERMIT_LIMITS["cu_ppb"], line_dash="dash", annotation_text="Cu permit")
    st.plotly_chart(fig, use_container_width=True)

    f_times = [datetime.fromisoformat(p["timestamp"]) for p in forecast["points"]]
    f_fig = go.Figure()
    f_fig.add_trace(go.Scatter(x=f_times, y=[p["predicted_cu_ppb"] for p in forecast["points"]], name="Forecast Cu"))
    f_fig.add_trace(
        go.Scatter(x=f_times, y=[p["predicted_chlorine_mgL"] for p in forecast["points"]], name="Forecast Chlorine")
    )
    f_fig.add_hline(y=DEFAULT_PERMIT_LIMITS["cu_ppb"], line_dash="dash", annotation_text="Cu permit")
    f_fig.add_hline(y=DEFAULT_PERMIT_LIMITS["trc_mgL"], line_dash="dot", annotation_text="TRC permit")
    st.plotly_chart(f_fig, use_container_width=True)

with col4:
    st.subheader("Panel 4 - AI Recommendations")
    rec = history[-1].get("recommendation") if history else None
    if rec:
        st.metric("Blowdown", f"{rec['recommended_blowdown_rate_m3_day']:.1f} m3/day")
        st.metric("Biocide Dose", f"{rec['recommended_biocide_dose_mgL']:.2f} mg/L")
        st.metric("pH Setpoint", f"{rec['recommended_ph_setpoint']:.2f}")
        st.metric("CoC Target", f"{rec['recommended_coc_target']:.2f}")
        st.write("Reasoning:")
        for line in rec.get("reasoning", []):
            st.write(f"- {line}")
        st.caption(
            "Permit anchors: "
            f"Cu <= {DEFAULT_PERMIT_LIMITS['cu_ppb']} ppb, "
            f"Zn <= {DEFAULT_PERMIT_LIMITS['zn_ppb']} ppb, "
            f"TRC <= {DEFAULT_PERMIT_LIMITS['trc_mgL']} mg/L"
        )
    else:
        st.info("Model recommendation not available yet.")
