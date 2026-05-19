import streamlit as st
import pandas as pd
import time
from config.settings import settings
from core.llm_governor import LlmGovernor
from core.safety_matrix import ActuationSafetyMatrix
from telemetry.mock_sensors import RealTimeTelemetryEngine

# Page Layout Configuration and Industrial Terminal CSS Styling Injection
st.set_page_config(page_title="NEXUS-FLOW // MASTER OS", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    * { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background-color: #0A0A0B; color: #00FF66; }
    div[data-testid="stMetricValue"] { color: #00FF66; font-size: 2.2rem; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: #8A9A86; font-size: 0.85rem; }
    .reportview-container .main .block-container { max-width: 95%; }
    .override-box { background-color: #2A080C; border: 1px solid #FF3344; padding: 15px; border-radius: 4px; color: #FF3344; margin-bottom: 20px; }
    .nominal-box { background-color: #051A10; border: 1px solid #00FF66; padding: 15px; border-radius: 4px; color: #00FF66; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# State Management Initialization
if "governor" not in st.session_state:
    st.session_state.governor = LlmGovernor()
    st.session_state.sensors = RealTimeTelemetryEngine()
    st.session_state.current_actuation = {
        "pump_pressure_psi": 30.0, 
        "coolant_flow_lpm": 15.0, 
        "valve_actuation_pct": 50.0, 
        "justification": "System boot initialization completed."
    }
    st.session_state.history = []

# Main Terminal Header Banner
st.title("⚡ NEXUS-FLOW // SOVEREIGN ENGINE GOVERNOR")
st.caption(f"PRODUCTION AUTOMATION WORKLOAD PLATFORM // ACTIVE MODEL: {settings.MODEL_NAME.upper()}")
st.markdown("---")

# Execution Pipeline Loop Processing
telemetry_data = st.session_state.sensors.read_sensors(st.session_state.current_actuation)
proposed_strategy = st.session_state.governor.compute_optimization_strategy(telemetry_data)
sanitized_strategy, override_triggered = ActuationSafetyMatrix.verify_action(
    proposed_strategy, telemetry_data["gpu_rack_temperature_c"]
)

# Commit Current Cycle Values Back to State Logs
st.session_state.current_actuation = sanitized_strategy
st.session_state.history.append({**telemetry_data, **sanitized_strategy})
if len(st.session_state.history) > 30: 
    st.session_state.history.pop(0)

# Multi-Column High Density Telemetry Layout Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="GPU RACK CORE THERMALS", value=f"{telemetry_data['gpu_rack_temperature_c']} °C")
with col2:
    st.metric(label="FLUID OUTFLOW PRESSURE", value=f"{telemetry_data['fluid_return_pressure_psi']} PSI")
with col3:
    st.metric(label="COOLANT LOOP VELOCITY", value=f"{sanitized_strategy['coolant_flow_lpm']} LPM")
with col4:
    st.metric(label="VALVE ACTUATION RATIO", value=f"{sanitized_strategy['valve_actuation_pct']} %")

st.markdown("### SYSTEM REASONING & ACTUATION LOGS")

# Dynamic Firewall Visual Indicators Banner
if override_triggered:
    st.markdown(f"""<div class='override-box'><strong>⚠️ AIR-GAP CRITICAL INTERVENTION DETECTED:</strong> Low-level physics engine overrode autonomous commands to prevent physical system degradation.</div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div class='nominal-box'><strong>🟢 ACTUATION STATE NOMINAL:</strong> Autonomous system parameters completely authenticated via safety matrix validation.</div>""", unsafe_allow_html=True)

st.info(f"**Autonomous Strategy Justification:** {sanitized_strategy['justification']}")

# Real-Time Telemetry Matrix Ledger
df = pd.DataFrame(st.session_state.history)
if not df.empty:
    st.markdown("### LIVE TELEMETRY MATRIX LOG")
    st.dataframe(df[['timestamp', 'gpu_rack_temperature_c', 'fluid_return_pressure_psi', 'coolant_flow_lpm', 'valve_actuation_pct']].tail(10), use_container_width=True)

# Fixed Latency Refresh Loop Engine Call
time.sleep(1.2)
st.rerun()
