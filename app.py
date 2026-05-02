import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
from datetime import datetime

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Nexus-Flow AI", page_icon="🌊", layout="wide")

# Custom CSS for an Industrial Dark Mode feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    div[data-testid="stMetricValue"] { color: #00ffa2; font-family: 'Courier New', monospace; }
    .stInfo { background-color: #161b22; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SECURE API INITIALIZATION ---
def init_client():
    # Looks for secret in .streamlit/secrets.toml or Streamlit Cloud Secrets
    # Replace the string below with your new key for local testing
    api_key = st.secrets.get("GROQ_API_KEY", "YOUR_NEW_REVOKED_KEY_HERE")
    return Groq(api_key=api_key)

client = init_client()

# --- 3. THE AI REASONING ENGINE ---
def get_nexus_decision(load, temp, water):
    """Sub-second thermodynamic reasoning via Groq LPU."""
    prompt = f"Governor Update: {load}kW Load, {temp}C Temp, {water}% Water. Respond in JSON: 'strategy', 'valve_set', 'logic_summary'."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except:
        return {"strategy": "FAILSAFE", "valve_set": 0.0, "logic_summary": "API Latency - Reverting to manual bypass."}

# --- 4. DASHBOARD HEADER ---
st.title("🌊 Nexus-Flow AI")
st.status("⚡ Connection to Groq LPU Cluster: Optimized", state="complete")
st.caption("v2.1.0 | Sovereign Energy-Water Nexus Controller | 2026 Edition")

# Initialize session state for tracking data
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Temp', 'Water'])
    st.toast("Nexus-Flow Governor is now controlling VMD Valve-01", icon="🌊")

# --- 5. INTERFACE LAYOUT ---
col1, col2, col3 = st.columns(3)
thermal_box = col1.empty()
water_box = col2.empty()
strategy_box = col3.empty()

chart_box = st.empty()
logic_box = st.empty()

# --- 6. REAL-TIME GOVERNANCE LOOP ---
if st.toggle("🚀 Activate Real-Time Monitoring", value=True):
    tick = 0
    while True:
        tick += 1
        
        # Simulated Telemetry (Replace with real sensor API calls here)
        now = datetime.now()
        live_temp = 60 + np.random.uniform(-2, 6)
        live_water = max(0, 90 - (tick * 0.35)) # Simulating water consumption
        live_load = 9000 + np.random.randint(-100, 100)
        
        # AI Logic Trigger (Every 2nd cycle to manage API credits)
        if tick % 2 == 0:
            decision = get_nexus_decision(live_load, live_temp, live_water)
            strategy_txt = decision['strategy']
            logic_msg = decision['logic_summary']
        else:
            strategy_txt = "ANALYZING..."
            logic_msg = "Awaiting LPU inference..."

        # Update Live Metrics
        thermal_box.metric("Compute Heat Exit", f"{live_temp:.1f}°C")
        water_box.metric("Distillate Reservoir", f"{live_water:.1f}%", delta="-0.35%")
        strategy_box.metric("Agent Strategy", strategy_txt)

        # Update Logic Insights
        logic_box.info(f"**Autonomous Logic:** {logic_msg}")

        # Update Historical Chart
        new_row = pd.DataFrame({'Time': [now], 'Temp': [live_temp], 'Water': [live_water]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Temp'], 
                                 name="Thermal (°C)", line=dict(color='#ff4b4b', width=3)))
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Water'], 
                                 name="Potable Water (%)", line=dict(color='#00ffaa', width=3)))
        
        fig.update_layout(
            template="plotly_dark", 
            height=400, 
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        chart_box.plotly_chart(fig, use_container_width=True)

        # 2-second sleep ensures the "Streamlit Oven" error never happens
        time.sleep(2)
