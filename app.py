import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
from datetime import datetime

# --- 1. SYSTEM CONFIG & CLEAN THEME ---
st.set_page_config(page_title="NEXUS-FLOW // HUD", page_icon="📟", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0a0a0a;
        color: #00ffa2;
    }
    
    .stMetric {
        background: rgba(0, 255, 162, 0.05);
        border: 1px solid #00ffa2;
        padding: 15px;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -1px;
        border-left: 10px solid #00ffa2;
        padding-left: 20px;
        margin-bottom: 20px;
    }
    
    .stInfo { background-color: #111; border: 1px solid #00ffa2; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CLEAN HEADER ---
st.markdown('<div class="main-title">NEXUS-FLOW_OS v4.2</div>', unsafe_allow_html=True)
st.caption("INDUSTRIAL DC2P GOVERNOR // ENCRYPTED LINK // NODE_01")

# --- 3. CORE INITIALIZATION ---
def get_client():
    # Priority: Secrets -> Fallback
    key = st.secrets.get("GROQ_API_KEY", "YOUR_KEY_HERE")
    return Groq(api_key=key)

client = get_client()

if 'packet_buffer' not in st.session_state:
    st.session_state.packet_buffer = []
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['T', 'W'])

# --- 4. TOP-LEVEL TELEMETRY ---
st.status("LPU_LINK: SECURED // DATA_CENTER_GOVERNOR: ACTIVE", state="complete")
m1, m2, m3, m4 = st.columns(4)
thermal_ui = m1.empty()
water_ui = m2.empty()
load_ui = m3.empty()
health_ui = m4.empty()

st.divider()

# --- 5. DATA VISUALIZATION ---
col_graph, col_logs = st.columns([2, 1])

with col_graph:
    st.markdown("### 📡 THERMAL_GRADIENT_SYNC")
    chart_ui = st.empty()

with col_logs:
    st.markdown("### 🧠 GOVERNOR_LOGIC")
    logic_ui = st.empty()
    st.markdown("### 📟 RAW_STREAM")
    packet_ui = st.empty()

# --- 6. EXECUTION LOOP ---
if st.toggle("INITIALIZE_NEXUS", value=True):
    for i in range(2000):
        # Hardware Simulation
        t = 64 + (np.sin(i/10) * 12) + np.random.normal(0, 0.4)
        w = max(0, 100 - (i * 0.2))
        load = 9400 + np.random.randint(-100, 100)
        
        # Packet Logging
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        pkt = f"[{ts}] RX >> T:{t:.1f}C | W:{w:.1f}% | L:{load}kW"
        st.session_state.packet_buffer.insert(0, pkt)
        
        # AI Logic Trigger (Every 5 ticks)
        if i % 5 == 0:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Status: {t}C, {w}%. Output JSON: 'act', 'msg'."}],
                    response_format={"type": "json_object"}
                )
                intel = json.loads(res.choices[0].message.content)
                logic_ui.info(f"**ACTION:** {intel['act']}\n\n**LOG:** {intel['msg']}")
            except: pass

        # Update Live Metrics
        thermal_ui.metric("CORE_TEMP", f"{t:.1f}°C")
        water_ui.metric("RESERVOIR", f"{w:.1f}%", delta="-0.2%")
        load_ui.metric("GRID_LOAD", f"{load} kW")
        status = "🟢 STABLE" if t < 80 else "🔴 WARNING"
        health_ui.metric("HEALTH", status)

        # Update Chart
        new_row = pd.DataFrame({'T': [t], 'W': [w]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(50)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=st.session_state.history['T'], name="HEAT", 
                                 line=dict(color='#00ffa2', width=4), fill='tozeroy'))
        fig.add_trace(go.Scatter(y=st.session_state.history['W'], name="WATER", 
                                 line=dict(color='#0066ff', width=2, dash='dot')))
        
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=0,r=0,t=0,b=0), 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        chart_ui.plotly_chart(fig, use_container_width=True)

        # Update Packets
        packet_ui.code("\n".join(st.session_state.packet_buffer[:8]), language="bash")
        
        time.sleep(1.2)
