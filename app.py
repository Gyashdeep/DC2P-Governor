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
        background: rgba(0, 255, 162, 0.03);
        border: 1px solid #00ffa2;
        box-shadow: inset 0 0 15px #00ffa211;
        padding: 10px;
    }

    .ascii-header {
        font-family: 'Share Tech Mono', monospace; 
        color: #00ffa2; 
        font-size: 7px; 
        line-height: 1.0; 
        white-space: pre; 
        text-align: center; 
        text-shadow: 0 0 10px #00ffa2;
        margin-bottom: 25px;
        filter: brightness(1.2);
    }
    
    .stInfo { background-color: #111; border: 1px solid #00ffa2; }
    </style>
""", unsafe_allow_html=True)

# --- 2. STABILIZED ASCII LOGO ---
st.markdown("""<div class="ascii-header">
    _   _  _______  __  __ _   _  ____        _____ _      ______          __
   | \ | |  ____| \/  | | | | / ___|      |  ___| |    / __ \ \        / /
   |  \| | |__   \  / /| | | | \___ \ _____| |_  | |   | |  | \ \  /\  / / 
   | . ` |  __|   >  < | | | |  ___) |_____|  _| | |   | |  | |\ \/  \/ /  
   | |\  | |____ /  /\ \ |_| | |____/      | |   | |___| |__| | \  /\  /   
   |_| \_|______/_/  \_\_____/|_____/       |_|   |______\____/   \/  \/    
                                                                           
   >> SYSTEM_ID: NEXUS-FLOW_v4.2 // STATUS: ACTIVE // ENCRYPT: AES-256
   -------------------------------------------------------------------------
</div>""", unsafe_allow_html=True)

# --- 3. CORE INITIALIZATION ---
def get_client():
    # Looks for secret in .streamlit/secrets.toml
    key = st.secrets.get("GROQ_API_KEY", "PASTE_NEW_KEY_HERE_FOR_LOCAL_RUN")
    return Groq(api_key=key)

client = get_client()

if 'packet_buffer' not in st.session_state:
    st.session_state.packet_buffer = []
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['T', 'W'])

# --- 4. HUD TELEMETRY ---
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
    # Professional Toast on Launch
    st.toast("Establishing connection to LPU Cluster...", icon="⚡")
    
    for i in range(2000):
        # Hardware Simulation
        t = 65 + (np.sin(i/8) * 10) + np.random.normal(0, 0.3)
        w = max(0, 100 - (i * 0.15))
        load = 9200 + np.random.randint(-150, 150)
        
        # Log Packet Generation
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        pkt = f"[{ts}] RX_DATA >> T:{t:.1f}C | W:{w:.1f}% | L:{load}kW"
        st.session_state.packet_buffer.insert(0, pkt)
        
        # AI Governor Reasoning (Every 5 ticks to stay in Free Tier limits)
        if i % 5 == 0:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"DATA: {t}C, {w}%. Respond JSON: 'act' (Action), 'log' (Logic)."}],
                    response_format={"type": "json_object"}
                )
                intel = json.loads(res.choices[0].message.content)
                logic_ui.info(f"**CMD:** {intel['act']}\n\n**LOG:** {intel['log']}")
            except: 
                pass

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
        # Glowing Area Chart for Thermal
        fig.add_trace(go.Scatter(y=st.session_state.history['T'], name="HEAT", 
                                 line=dict(color='#00ffa2', width=3), 
                                 fill='tozeroy', fillcolor='rgba(0, 255, 162, 0.1)'))
        
        fig.add_trace(go.Scatter(y=st.session_state.history['W'], name="WATER", 
                                 line=dict(color='#0066ff', width=2, dash='dot')))
        
        fig.update_layout(
            template="plotly_dark", 
            height=400, 
            margin=dict(l=0,r=0,t=0,b=0), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        chart_ui.plotly_chart(fig, use_container_width=True)

        # Update Packet Stream
        packet_ui.code("\n".join(st.session_state.packet_buffer[:10]), language="bash")
        
        # 1.5s delay provides real-time feel without crashing the browser
        time.sleep(1.5)
