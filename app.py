import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
from datetime import datetime

# --- 1. SYSTEM CONFIG & INDUSTRIAL THEME ---
st.set_page_config(page_title="NEXUS-FLOW // MASTER", page_icon="📟", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #050505;
        color: #00ffa2;
    }
    
    .stMetric {
        background: rgba(0, 255, 162, 0.05);
        border: 1px solid #00ffa2;
        padding: 10px;
        box-shadow: inset 0 0 10px #00ffa211;
    }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        border-left: 8px solid #00ffa2;
        padding-left: 15px;
        margin-bottom: 5px;
        text-shadow: 0 0 10px #00ffa244;
    }
    
    .stInfo { background-color: #111; border: 1px solid #00ffa2; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown('<div class="main-title">NEXUS-FLOW // MASTER_OS v4.5</div>', unsafe_allow_html=True)
st.caption("AI-GOVERNED THERMAL MANAGEMENT // LPU-ACCELERATED // 2026 STABLE")

# --- 3. CORE INITIALIZATION (SECURED) ---
def get_client():
    # Looks for 'GROQ_API_KEY' in Streamlit Secrets or Local secrets.toml
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        st.error("🔑 API KEY NOT FOUND. PLEASE ADD 'GROQ_API_KEY' TO STREAMLIT SECRETS.")
        st.stop()
    return Groq(api_key=key)

client = get_client()

if 'packet_buffer' not in st.session_state:
    st.session_state.packet_buffer = []
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['T', 'W'])

# --- 4. BOOT SEQUENCE & TELEMETRY LAYOUT ---
with st.status("ESTABLISHING LPU_LINK...", state="running") as status:
    st.write("Verifying Credentials...")
    time.sleep(0.4)
    st.write("Handshaking with Llama-3.3-70B...")
    time.sleep(0.4)
    status.update(label="LPU_LINK: SECURED // GOVERNOR_MODEL: LLAMA-3.3-70B", state="complete")

col_gauge, col_metrics = st.columns([1, 2])
gauge_placeholder = col_gauge.empty()

with col_metrics:
    m_top1, m_top2 = st.columns(2)
    m_bot1, m_bot2 = st.columns(2)
    thermal_ui = m_top1.empty()
    water_ui = m_top2.empty()
    load_ui = m_bot1.empty()
    health_ui = m_bot2.empty()

st.divider()

# --- 5. DATA VISUALIZATION LAYOUT ---
col_graph, col_logs = st.columns([2, 1])

with col_graph:
    st.markdown("### 📡 THERMAL_SYNC_MAP")
    chart_ui = st.empty()

with col_logs:
    st.markdown("### 🧠 GOVERNOR_LOGIC")
    logic_ui = st.empty()
    st.markdown("### 📟 RAW_STREAM")
    packet_ui = st.empty()

# --- 6. EXECUTION LOOP ---
if st.toggle("ACTIVATE_NEXUS_LINK", value=True):
    for i in range(10000):
        # Hardware Simulation Logic
        t = 65 + (np.sin(i/10) * 15) + np.random.normal(0, 0.5)
        w = max(0, 100 - (i * 0.12))
        load = 9200 + np.random.randint(-200, 200)
        
        # A. Update Radial Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = t,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "THERMAL_PRESSURE", 'font': {'size': 14, 'color': "#00ffa2"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "#00ffa2"},
                'bar': {'color': "#00ffa2"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#00ffa2",
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(0, 255, 162, 0.1)'},
                    {'range': [60, 85], 'color': 'rgba(255, 165, 0, 0.2)'},
                    {'range': [85, 100], 'color': 'rgba(255, 0, 0, 0.3)'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'value': 90}
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#00ffa2"}, height=240, margin=dict(l=20,r=20,t=40,b=20))
        gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True)

        # B. Update Metrics
        thermal_ui.metric("CORE_TEMP", f"{t:.1f}°C")
        water_ui.metric("RESERVOIR", f"{w:.1f}%", delta="-0.12%")
        load_ui.metric("GRID_LOAD", f"{load} kW")
        status_text = "🟢 NOMINAL" if t < 80 else "🔴 CRITICAL"
        health_ui.metric("SYSTEM_HEALTH", status_text)

        # C. AI Logic (Every 5 ticks to save API tokens)
        if i % 5 == 0:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Status: {t}C, {w}%. Respond in JSON with keys 'act' and 'msg'."}],
                    response_format={"type": "json_object"}
                )
                intel = json.loads(res.choices[0].message.content)
                logic_ui.info(f"**ACTION:** {intel['act']}\n\n**LOG:** {intel['msg']}")
            except Exception as e:
                logic_ui.error("LPU CONNECTION INTERRUPTED")

        # D. Update Historical Chart
        new_row = pd.DataFrame({'T': [t], 'W': [w]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(40)
        
        fig_map = go.Figure()
        fig_map.add_trace(go.Scatter(y=st.session_state.history['T'], name="HEAT", 
                                     line=dict(color='#00ffa2', width=4), fill='tozeroy'))
        fig_map.add_trace(go.Scatter(y=st.session_state.history['W'], name="WATER", 
                                     line=dict(color='#0066ff', width=2, dash='dot')))
        fig_map.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        chart_ui.plotly_chart(fig_map, use_container_width=True)

        # E. Update Packet Stream
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        st.session_state.packet_buffer.insert(0, f"[{ts}] RX >> T:{t:.1f} | W:{w:.1f}%")
        packet_ui.code("\n".join(st.session_state.packet_buffer[:7]), language="bash")
        
        time.sleep(1.0)
