import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Nexus-Flow AI", page_icon="🌊", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# --- SECURE API CLIENT ---
def init_client():
    # Priority: st.secrets -> Then fallback string for local testing
    api_key = st.secrets.get("GROQ_API_KEY", "YOUR_NEW_KEY_HERE")
    return Groq(api_key=api_key)

client = init_client()

# --- AGENTIC ENGINE ---
def get_nexus_decision(load, temp, water):
    """Reasoning engine using Groq Llama 3.3 70B for speed."""
    prompt = f"System: DC2P Governor. Input: {load}kW, {temp}C, {water}% water. Task: Output JSON: 'strategy', 'valve', 'logic'."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except:
        return {"strategy": "STABLE", "valve": 0.5, "logic": "Failsafe active."}

# --- DASHBOARD LAYOUT ---
st.title("🌊 Nexus-Flow AI")
st.caption("Autonomous Data-Center-to-Potable (DC2P) Energy Governor | v1.2.0")

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Temp', 'Water'])

# --- CONTROL PANEL ---
col_m1, col_m2, col_m3 = st.columns(3)
thermal_metric = col_m1.empty()
water_metric = col_m2.empty()
strategy_metric = col_m3.empty()

chart_container = st.empty()
log_container = st.empty()

# --- LIVE EXECUTION LOOP ---
# The toggle prevents the app from starting heavy tasks until you are ready
if st.toggle("🛰️ Establish Real-Time Link", value=True):
    step = 0
    while True:
        step += 1
        
        # 1. SIMULATED DATA (Replace with MQTT/Modbus calls in production)
        now = datetime.now()
        current_temp = 62 + np.random.uniform(-1, 4)
        current_water = max(0, 85 - (step * 0.4))
        current_load = 9200 + np.random.randint(-150, 150)
        
        # 2. AGENT REASONING (Every 4 seconds to prevent API throttling)
        if step % 2 == 0:
            decision = get_nexus_decision(current_load, current_temp, current_water)
            log_container.info(f"**Nexus Logic:** {decision['logic']}")
            strategy_val = decision['strategy']
        else:
            strategy_val = "CALCULATING..."

        # 3. UPDATE UI COMPONENTS
        thermal_metric.metric("Thermal Energy", f"{current_temp:.1f}°C")
        water_metric.metric("Water Reservoir", f"{current_water:.1f}%", delta="-0.4%")
        strategy_metric.metric("AI Strategy", strategy_val)

        # 4. CHART UPDATES
        new_data = pd.DataFrame({'Time': [now], 'Temp': [current_temp], 'Water': [current_water]})
        st.session_state.history = pd.concat([st.session_state.history, new_data]).tail(25)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Temp'], name="Thermal", line=dict(color='#ff4b4b')))
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Water'], name="Water", line=dict(color='#00ffaa')))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h"))
        
        chart_container.plotly_chart(fig, use_container_width=True)

        # 5. PACING (Crucial to prevent 'App Over-capacity')
        time.sleep(2)
