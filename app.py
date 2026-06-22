import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="TrackGuard AI Command Center",
    page_icon="🚆",
    layout="wide"
)

# ----------------------------
# Load Detection Data
# ----------------------------

log_file = "database/detection_history.csv"

if os.path.exists(log_file):
    df = pd.read_csv(log_file)

    total_scans = len(df)

    defects = len(df[df["Class"] == "defective"])

    safe_tracks = len(df[df["Class"] == "non-defective"])

    system_health = round(
        (safe_tracks / total_scans) * 100,
        1
    ) if total_scans > 0 else 100

else:
    total_scans = 0
    defects = 0
    safe_tracks = 0
    system_health = 100

# ----------------------------
# Styling
# ----------------------------

st.markdown("""
<style>

/* ── Base ── */
.main { background-color: #0E1117; }

/* ── Hero ── */
.hero {
    padding: 30px 35px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2a1e 100%);
    border: 1px solid #334155;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 44px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.hero-sub {
    font-size: 17px;
    color: #94a3b8;
    margin-top: 8px;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    margin-top: 14px;
    padding: 5px 14px;
    background: rgba(34,197,94,0.15);
    border: 1px solid rgba(34,197,94,0.4);
    border-radius: 50px;
    color: #4ade80;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── KPI Cards ── */
.card {
    background: linear-gradient(145deg, #1E293B, #162032);
    padding: 22px 20px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #334155;
    border-left: 4px solid var(--accent, #4ade80);
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    transition: border-color 0.2s, transform 0.2s;
}
.card:hover { border-color: #4ade80; transform: translateY(-2px); }
.card-value {
    font-size: 36px;
    font-weight: 800;
    color: white;
    line-height: 1.1;
}
.card-value.accent { color: #4ade80; }
.card-value.warn   { color: #f87171; }
.card-label {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-top: 6px;
}
.card-icon {
    font-size: 20px;
    margin-bottom: 8px;
}

/* ── Section Headers ── */
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: white;
    padding-bottom: 10px;
    border-bottom: 2px solid #1e293b;
    margin-bottom: 16px;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155, transparent);
    margin: 28px 0;
}

/* ── Executive Glass Card ── */
.glass-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.85), rgba(15,23,42,0.9));
    backdrop-filter: blur(10px);
    border-radius: 22px;
    padding: 28px 32px;
    border: 1px solid rgba(148,163,184,0.18);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.glass-card-label {
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.glass-card-value {
    font-size: 52px;
    font-weight: 800;
    line-height: 1;
}
.glass-card-sub {
    margin-top: 14px;
    display: flex;
    gap: 28px;
    flex-wrap: wrap;
}
.glass-card-sub-item { font-size: 13px; color: #cbd5e1; }
.glass-card-sub-item strong { display: block; font-size: 14px; }

/* ── System Status Cards ── */
.status-card {
    background: linear-gradient(160deg, #1a2335, #131b2b);
    border-radius: 16px;
    padding: 20px 22px;
    border: 1px solid #2a3650;
    border-left: 4px solid #4ade80;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    height: 100%;
}
.status-card-title {
    font-size: 15px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}
.status-dot {
    display:inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ade80;
    margin-right: 8px;
    box-shadow: 0 0 6px rgba(74,222,128,0.6);
}
.status-text {
    color: #4ade80;
    font-weight: 600;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar Branding
# ----------------------------

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 16px 0;">
      <div style="font-size:26px; font-weight:800; color:white; line-height:1.2;">🚆 TRACKGUARD AI</div>
      <div style="font-size:12px; color:#94a3b8; margin-top:4px; letter-spacing:0.3px;">
        Railway Infrastructure Intelligence Platform
      </div>
    </div>
    <div class="divider" style="margin: 0 0 18px 0;"></div>
    """, unsafe_allow_html=True)

# ----------------------------
# Hero Section
# ----------------------------

st.markdown("""
<div class="hero">
  <div class="hero-title">🚆 TRACKGUARD AI COMMAND CENTER</div>
  <div class="hero-sub">AI Railway Infrastructure Monitoring &amp; Risk Intelligence Platform</div>
  <div class="hero-badge">🟢 System Online</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Executive Overview
# ----------------------------

st.markdown('<div class="section-header">📊 Executive Overview</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="glass-card">
  <div class="glass-card-label">System Health</div>
  <div class="glass-card-value" style="color:{'#4ade80' if system_health >= 80 else ('#fbbf24' if system_health >= 50 else '#f87171')};">{system_health}%</div>
  <div class="glass-card-sub">
    <div class="glass-card-sub-item">Total Scans<strong style="color:#e2e8f0;">{total_scans}</strong></div>
    <div class="glass-card-sub-item">Defects Detected<strong style="color:#f87171;">{defects}</strong></div>
    <div class="glass-card-sub-item">Safe Tracks<strong style="color:#4ade80;">{safe_tracks}</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# KPI Cards
# ----------------------------

st.markdown('<div class="section-header">🧭 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="--accent:#60a5fa;">
      <div class="card-icon">🔍</div>
      <div class="card-value">{total_scans}</div>
      <div class="card-label">Total Scans</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="--accent:#f87171;">
      <div class="card-icon">⚠️</div>
      <div class="card-value warn">{defects}</div>
      <div class="card-label">Defects Detected</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="--accent:#4ade80;">
      <div class="card-icon">✅</div>
      <div class="card-value accent">{safe_tracks}</div>
      <div class="card-label">Safe Tracks</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="--accent:#4ade80;">
      <div class="card-icon">🟢</div>
      <div class="card-value accent">{system_health}%</div>
      <div class="card-label">System Health</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# System Status
# ----------------------------

st.markdown('<div class="section-header">🖥️ System Status</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="status-card">
      <div class="status-card-title">🧠 YOLO Model</div>
      <div><span class="status-dot"></span><span class="status-text">LOADED</span></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="status-card">
      <div class="status-card-title">⚙️ Detection Engine</div>
      <div><span class="status-dot"></span><span class="status-text">ACTIVE</span></div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="status-card">
      <div class="status-card-title">🗄️ Database</div>
      <div><span class="status-dot"></span><span class="status-text">CONNECTED</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# Recent Activity
# ----------------------------

st.markdown('<div class="section-header">📋 Recent Detection Activity</div>', unsafe_allow_html=True)

if os.path.exists(log_file):

    st.dataframe(
        df.tail(10),
        use_container_width=True
    )

else:

    st.info(
        "No detection history available."
    )

# ----------------------------
# Footer
# ----------------------------

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#334155; font-size:12px; padding-bottom:20px;">
  TrackGuard AI &nbsp;•&nbsp; Railway Infrastructure Intelligence Platform
</div>
""", unsafe_allow_html=True)