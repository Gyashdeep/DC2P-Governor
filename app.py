import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import json
import time
from datetime import datetime

# --- 1. HUD & THEME CONFIG ---
st.set_page_config(page_title="NEXUS-FLOW // MASTER", page_icon="📟", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', monospace;
        background-color: #050505;
        color: #00ffa2;
    }
    .stMetric {
        background: rgba(0, 255, 162, 0.05);
        border: 1px solid #00ffa2;
        box-shadow: inset 0 0 15px #00ffa222;
    }
    .ascii-header {
        color: #00ffa2;
        line-height: 1;
        font-size: 8px;
        white-space: pre;
        text-shadow: 0 0 8px #00ffa2;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. THE RETURN OF ASCII ---
st.markdown("""<div class="ascii-header">
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗      ███████╗██╗      ██████╗ ██╗    ██╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝      ██╔════╝██║     ██╔═══██╗██║    ██║
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗█████╗█████╗  ██║     ██║   ██║██║ █╗ ██║
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║╚════╝██╔══╝  ██║     ██║   ██║██║███╗██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║      ██║     ███████╗╚██████╔╝╚███╔███╔╝
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝      ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝
</div>""", unsafe_allow_html=True)

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
st.status("CORE_SYSTEM: ONLINE // LPU_LINK: SECURED // DC2P_GOVERNOR: READY", state="complete")
m1, m2, m3, m4 = st.columns(4)
thermal_ui = m1.empty()
water_ui = m2.empty()
load_ui = m3.empty()
health_ui = m4.empty()

st.divider()

# --- 5. MAIN CONSOLE LAYOUT ---
col_map, col_data = st.columns([2, 1])

with col_map:
    st.markdown("### 📡 REAL-TIME THERMAL GRADIENT")
    chart_ui = st.empty()

with col_data:
    st.markdown("### 🧠 AGENT_COGNITION")
    logic_ui = st.empty()
    st.markdown("### 📟 RAW_PACKET_STREAM")
    packet_ui = st.empty()

# --- 6. EXECUTION LOOP ---
if st.toggle("INITIALIZE NEXUS-LINK", value=True):
    for i in range(1000):
        # Hardware Simulation
        t = 65 + (np.sin(i/8) * 10) + np.random.normal(0, 0.3)
        w = max(0, 100 - (i * 0.15))
        load = 8800 + np.random.randint(-200, 200)
        
        # Log Packet Generation
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        pkt = f"[{ts}] RX_DATA >> T:{t:.1f}C | W:{w:.1f}% | L:{load}kW"
        st.session_state.packet_buffer.insert(0, pkt)
        
        # AI Governor Reasoning (Every 5 ticks)
        if i % 5 == 0:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"DATA: {t}C, {w}%. Respond JSON: 'act' (Action), 'log' (Logic)."}],
                    response_format={"type": "json_object"}
                )
                intel = json.loads(res.choices[0].message.content)
                logic_ui.info(f"**CMD:** {intel['act']}\n\n**LOG:** {intel['log']}")
            except: pass

        # Update Metrics
        thermal_ui.metric("CORE_TEMP", f"{t:.1f}°C")
        water_ui.metric("RESERVOIR", f"{w:.1f}%", delta="-0.15%")
        load_ui.metric("GRID_LOAD", f"{load} kW")
        status = "🟢 NOMINAL" if t < 78 else "🔴 OVERHEAT"
        health_ui.metric("NODE_HEALTH", status)

        # Update Chart
        new_row = pd.DataFrame({'T': [t], 'W': [w]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(40)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=st.session_state.history['T'], name="HEAT", line=dict(color='#00ffa2', width=3), fill='tozeroy'))
        fig.add_trace(go.Scatter(y=st.session_state.history['W'], name="WATER", line=dict(color='#0066ff', width=2)))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        chart_ui.plotly_chart(fig, use_container_width=True)

        # Update Packets
        packet_ui.code("\n".join(st.session_state.packet_buffer[:10]), language="bash")
        
        time.sleep(1.5)
