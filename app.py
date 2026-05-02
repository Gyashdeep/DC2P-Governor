import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
import os
from datetime import datetime

# --- 1. SECURE API INITIALIZATION ---
def initialize_groq():
    # Priority 1: Streamlit Cloud Secrets
    # Priority 2: Local .streamlit/secrets.toml
    # Priority 3: System Environment Variables
    api_key = None
    
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        st.error("🔑 API Key Missing! Create .streamlit/secrets.toml or set GROQ_API_KEY env var.")
        st.stop()
        
    return Groq(api_key=api_key)

client = initialize_groq()

# --- 2. CONFIGURATION & UI ---
st.set_page_config(page_title="Autonomous DC2P Governor", layout="wide")
st.title("🌊 DC2P: Data-Center-to-Potable")
st.markdown("### *Autonomous Energy-Water Nexus Controller*")

# --- 3. AGENTIC REASONING ENGINE ---
def get_governor_decision(load, temp, water):
    """
    Calls the Groq Model (GPT-OSS 120B) to act as a 
    Thermodynamic Agent for Water Purification.
    """
    prompt = f"""
    SYSTEM: You are the DC2P Sovereign Governor.
    STATUS: GPU Load {load}kW | Coolant {temp}C | Water {water}%
    
    ACTION RULES:
    - If Water < 20%: Strategy = 'THERMAL_BURST' (Increase load).
    - If Temp > 75C: Strategy = 'EMERGENCY_THROTTLE'.
    - Else: Strategy = 'STEADY_STATE'.
    
    TASK: Output JSON with 'strategy', 'valve_pos' (0.0-1.0), and 'logic'.
    """
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"strategy": "FAILSAFE", "valve_pos": 0.0, "logic": f"System Error: {str(e)}"}

# --- 4. SIMULATION & DASHBOARD ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Temp', 'Water'])

placeholder = st.empty()

# Simulation loop (In production, replace with real MQTT sensor calls)
for i in range(50):
    with placeholder.container():
        # Simulated Hardware Telemetry
        sim_water = max(5, 45 - (i * 1.5))
        sim_load = 9000 + (np.random.randint(-200, 200))
        sim_temp = 58 + (i * 0.5)
        
        # AI Logic
        decision = get_governor_decision(sim_load, sim_temp, sim_water)
        
        # UI Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Thermal Energy (C)", f"{sim_temp:.1f}°C")
        c2.metric("Reservoir Level", f"{sim_water}%", delta="-1.5%")
        c3.metric("AI Strategy", decision['strategy'])
        
        # Real-time Reasoning Insight
        st.info(f"**Agent Logic:** {decision['logic']}")
        
        # Visualization
        new_entry = pd.DataFrame({'Time': [datetime.now()], 'Temp': [sim_temp], 'Water': [sim_water]})
        st.session_state.history = pd.concat([st.session_state.history, new_entry]).tail(15)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Temp'], name="Heat"))
        fig.add_trace(go.Scatter(x=st.session_state.history['Time'], y=st.session_state.history['Water'], name="Water"))
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(2)
