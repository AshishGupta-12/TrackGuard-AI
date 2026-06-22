import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="TrackGuard AI Command Center",
    page_icon="🚆",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
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
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    transition: border-color 0.2s;
}
.card:hover { border-color: #4ade80; }
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

/* ── Risk Panel ── */
.health-box {
    background: #111827;
    padding: 22px 24px;
    border-radius: 15px;
    border: 1px solid #1e293b;
    height: 100%;
}
.health-row {
    display: flex;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #1e293b;
    font-size: 14px;
    color: #cbd5e1;
}
.health-row:last-child { border-bottom: none; }
.health-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ade80;
    margin-right: 10px;
    box-shadow: 0 0 6px rgba(74,222,128,0.6);
    flex-shrink: 0;
}
.health-label { flex: 1; }
.health-status { color: #4ade80; font-weight: 600; font-size: 13px; }

/* ── Stats Grid ── */
.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 11px 0;
    border-bottom: 1px solid #1e293b;
    font-size: 14px;
}
.stat-row:last-child { border-bottom: none; }
.stat-key { color: #94a3b8; }
.stat-val { color: white; font-weight: 700; }

/* ── Alert Feed ── */
.alert-card {
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
    font-weight: 500;
}
.alert-defect {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.35);
    color: #fca5a5;
}
.alert-safe {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.3);
    color: #86efac;
}
.alert-meta { color: #64748b; font-size: 12px; margin-left: auto; white-space: nowrap; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155, transparent);
    margin: 28px 0;
}

/* ── Track Section Status Cards (new) ── */
.section-card {
    background: linear-gradient(160deg, #1a2335, #131b2b);
    border-radius: 16px;
    padding: 18px 20px;
    border: 1px solid #2a3650;
    border-left: 4px solid var(--status-color, #64748b);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    height: 100%;
}
.section-card-name {
    font-size: 17px;
    font-weight: 800;
    color: white;
    letter-spacing: 0.3px;
    margin-bottom: 10px;
}
.section-card-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin-bottom: 12px;
}
.section-card-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #94a3b8;
    padding: 5px 0;
}
.section-card-row span:last-child {
    color: #e2e8f0;
    font-weight: 600;
}

/* ── Executive Glass Card (new) ── */
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

/* ── Dangerous Section Highlight (new) ── */
.danger-highlight {
    background: linear-gradient(135deg, rgba(248,113,113,0.08), rgba(15,23,42,0.6));
    border: 1px solid rgba(248,113,113,0.35);
    border-radius: 18px;
    padding: 22px 24px;
}

/* ── Obstacle Panel (new) ── */
.obstacle-card {
    background: #111827;
    border-radius: 15px;
    border: 1px solid #1e293b;
    padding: 20px 22px;
    text-align: center;
}
.obstacle-value {
    font-size: 30px;
    font-weight: 800;
    color: #fbbf24;
}
.obstacle-label {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 4px;
}

</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
st.markdown("""
<div class="hero">
  <div class="hero-title">🚆 TRACKGUARD AI</div>
  <div class="hero-sub">
    Railway Infrastructure Intelligence Platform<br>
    Live Monitoring &nbsp;•&nbsp; AI Defect Detection &nbsp;•&nbsp; Risk Analytics
  </div>
  <div class="hero-badge">⬤ &nbsp;SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ---------- DATA LOADING ----------
log_file = "database/detection_history.csv"

df = pd.DataFrame()
total_events = 0
defects = 0
safe_tracks = 0
avg_risk_score = 0.0
avg_confidence = 0.0
defect_pct = 0.0
safe_pct = 0.0

if os.path.exists(log_file):
    df = pd.read_csv(log_file)
    total_events = len(df)
    defects = len(df[df["Class"] == "defective"])
    safe_tracks = len(df[df["Class"] != "defective"])

    # Average Risk Score
    if "RiskScore" in df.columns and total_events > 0:
        avg_risk_score = round(df["RiskScore"].mean(), 2)

    # Average Confidence
    if "Confidence" in df.columns and total_events > 0:
        try:
            conf_series = df["Confidence"].astype(str).str.replace("%", "").astype(float)
            avg_confidence = round(conf_series.mean(), 2)
        except Exception:
            avg_confidence = 0.0

    # Percentages
    if total_events > 0:
        defect_pct = round((defects / total_events) * 100, 1)
        safe_pct = round((safe_tracks / total_events) * 100, 1)

# ---------- HELPER FUNCTIONS (new) ----------

def get_latest_per_section(data: pd.DataFrame) -> pd.DataFrame:
    """Return the most recent row for each TrackSection, sorted by Time desc."""
    if data.empty or "TrackSection" not in data.columns:
        return pd.DataFrame()
    work = data.copy()
    if "Time" in work.columns:
        work["_TimeParsed"] = pd.to_datetime(work["Time"], errors="coerce")
        work = work.sort_values("_TimeParsed")
    latest = work.groupby("TrackSection", as_index=False).tail(1)
    if "_TimeParsed" in latest.columns:
        latest = latest.sort_values("_TimeParsed", ascending=False).drop(columns=["_TimeParsed"])
    return latest.reset_index(drop=True)


def section_status_color(level: str):
    """Map a RiskLevel string to (hex_color, label, emoji)."""
    if not isinstance(level, str):
        return ("#64748b", "UNKNOWN", "⚪")
    level_clean = level.strip().upper()
    mapping = {
        "SAFE":     ("#4ade80", "SAFE",     "🟢"),
        "LOW":      ("#4ade80", "LOW",      "🟢"),
        "MEDIUM":   ("#fbbf24", "MEDIUM",   "🟡"),
        "HIGH":     ("#fb923c", "HIGH",     "🟠"),
        "CRITICAL": ("#f87171", "CRITICAL", "🔴"),
    }
    return mapping.get(level_clean, ("#64748b", level_clean, "⚪"))


def get_most_dangerous_section(data: pd.DataFrame):
    """Return dict with the section having the highest average RiskScore, or None."""
    if data.empty or "TrackSection" not in data.columns or "RiskScore" not in data.columns:
        return None
    grouped = data.groupby("TrackSection").agg(
        AvgRiskScore=("RiskScore", "mean"),
        DefectCount=("Class", lambda s: (s == "defective").sum())
    ).reset_index()
    if grouped.empty:
        return None
    grouped = grouped.sort_values("AvgRiskScore", ascending=False)
    top = grouped.iloc[0]

    latest_level = "UNKNOWN"
    latest_rows = get_latest_per_section(data)
    if not latest_rows.empty and "RiskLevel" in latest_rows.columns:
        match = latest_rows[latest_rows["TrackSection"] == top["TrackSection"]]
        if not match.empty:
            latest_level = match.iloc[0].get("RiskLevel", "UNKNOWN")

    return {
        "section": top["TrackSection"],
        "avg_risk_score": round(top["AvgRiskScore"], 2),
        "defect_count": int(top["DefectCount"]),
        "latest_risk_level": latest_level
    }


def parse_obstacle_data(data: pd.DataFrame):
    """Compute obstacle stats from ObstacleCount / ObstacleTypes columns.
    Returns None if no usable obstacle data exists."""
    if data.empty or "ObstacleCount" not in data.columns:
        return None

    obs_counts = pd.to_numeric(data["ObstacleCount"], errors="coerce").fillna(0)
    total_obstacle_events = int((obs_counts > 0).sum())

    if total_obstacle_events == 0:
        return None

    most_common = None
    if "ObstacleTypes" in data.columns:
        types_series = data.loc[obs_counts > 0, "ObstacleTypes"].dropna().astype(str)
        # ObstacleTypes may be comma-separated per row (e.g. "person,debris")
        all_types = []
        for entry in types_series:
            parts = [p.strip() for p in entry.split(",") if p.strip()]
            all_types.extend(parts)
        if all_types:
            most_common = pd.Series(all_types).value_counts().idxmax()

    return {
        "total_events": total_obstacle_events,
        "most_common": most_common if most_common else "N/A",
        "total_obstacle_count": int(obs_counts.sum())
    }


def compute_health_score(avg_risk: float, data: pd.DataFrame) -> float:
    """Health Score = 100 - (avg_risk_score * 0.7) - (critical_alerts * 3), clamped to [0, 100]."""
    critical_alerts = 0
    if not data.empty and "RiskLevel" in data.columns:
        critical_alerts = int((data["RiskLevel"].astype(str).str.strip().str.upper() == "CRITICAL").sum())
    score = 100 - (avg_risk * 0.7) - (critical_alerts * 3)
    return max(0.0, min(100.0, round(score, 1))), critical_alerts


# ---------- NEW COMPUTED VALUES (real CSV data only) ----------
section_status_df = get_latest_per_section(df) if not df.empty else pd.DataFrame()
most_dangerous = get_most_dangerous_section(df) if not df.empty else None
obstacle_stats = parse_obstacle_data(df) if not df.empty else None
health_score, critical_alert_count = compute_health_score(avg_risk_score, df) if not df.empty else (0.0, 0)

# Health trend: compare avg risk score of the most recent half of records vs. earlier half
health_trend = "Insufficient data"
health_trend_color = "#64748b"
if not df.empty and "RiskScore" in df.columns and total_events >= 2:
    work = df.copy()
    if "Time" in work.columns:
        work["_TimeParsed"] = pd.to_datetime(work["Time"], errors="coerce")
        work = work.sort_values("_TimeParsed")
    midpoint = len(work) // 2
    earlier_half = work.iloc[:midpoint]
    recent_half = work.iloc[midpoint:]
    if not earlier_half.empty and not recent_half.empty:
        earlier_avg = earlier_half["RiskScore"].mean()
        recent_avg = recent_half["RiskScore"].mean()
        diff = recent_avg - earlier_avg
        if diff > 1:
            health_trend = f"Declining (Risk ↑ {round(diff,1)})"
            health_trend_color = "#f87171"
        elif diff < -1:
            health_trend = f"Improving (Risk ↓ {round(abs(diff),1)})"
            health_trend_color = "#4ade80"
        else:
            health_trend = "Stable"
            health_trend_color = "#94a3b8"

if health_score >= 80:
    health_status = "EXCELLENT"
    health_status_color = "#4ade80"
elif health_score >= 60:
    health_status = "GOOD"
    health_status_color = "#a3e635"
elif health_score >= 40:
    health_status = "FAIR"
    health_status_color = "#fbbf24"
else:
    health_status = "POOR"
    health_status_color = "#f87171"

# ---------- TIERED RISK LEVEL ----------
# Based on avg_risk_score rather than raw defect count,
# so 1 defect in 500 scans doesn't falsely trigger HIGH.
if avg_risk_score >= 70:
    risk_level = "HIGH"
    risk_level_color = "#f87171"    # red
    risk_level_icon  = "🔴"
elif avg_risk_score >= 40:
    risk_level = "MEDIUM"
    risk_level_color = "#fbbf24"    # amber
    risk_level_icon  = "🟡"
else:
    risk_level = "LOW"
    risk_level_color = "#4ade80"    # green
    risk_level_icon  = "🟢"

# ---------- KPI CARDS ----------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
      <div class="card-icon">📋</div>
      <div class="card-value">{total_events}</div>
      <div class="card-label">Total Events</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    val_class = "warn" if defects > 0 else "accent"
    st.markdown(f"""
    <div class="card">
      <div class="card-icon">🚨</div>
      <div class="card-value {val_class}">{defects}</div>
      <div class="card-label">Defects Found</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
      <div class="card-icon">✅</div>
      <div class="card-value accent">{safe_tracks}</div>
      <div class="card-label">Safe Tracks</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    risk_class = "warn" if risk_level == "HIGH" else ("" if risk_level == "MEDIUM" else "accent")
    risk_display = f"{avg_risk_score}" if total_events > 0 else "N/A"
    # For MEDIUM we inline the amber color directly since there's no CSS class for it
    risk_val_style = (
        'color:#fbbf24;' if risk_level == "MEDIUM" else ""
    )
    st.markdown(f"""
    <div class="card">
      <div class="card-icon">⚠️</div>
      <div class="card-value {risk_class}" style="{risk_val_style}">{risk_display}</div>
      <div class="card-label">Avg Risk Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- TRACK SECTION STATUS BOARD (new) ----------
st.markdown('<div class="section-header">🗺️ Track Section Status Board</div>', unsafe_allow_html=True)

if not section_status_df.empty and "TrackSection" in section_status_df.columns:
    sections = section_status_df["TrackSection"].tolist()
    cols = st.columns(min(len(sections), 4) if len(sections) > 0 else 1)

    for i, (_, row) in enumerate(section_status_df.iterrows()):
        col = cols[i % len(cols)]
        section_name = row.get("TrackSection", "—")
        risk_lvl = row.get("RiskLevel", "UNKNOWN")
        risk_scr = row.get("RiskScore", "—")
        last_time = row.get("Time", "—")

        color, label, emoji = section_status_color(risk_lvl)

        with col:
            st.markdown(f"""
            <div class="section-card" style="--status-color: {color};">
              <div class="section-card-name">📍 {section_name}</div>
              <div class="section-card-badge" style="background: {color}22; color: {color}; border: 1px solid {color}55;">{emoji} {label}</div>
              <div class="section-card-row"><span>Risk Score</span><span>{risk_scr}</span></div>
              <div class="section-card-row"><span>Last Inspection</span><span>{last_time}</span></div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No track section data found in detection_history.csv yet.")

st.write("")

# ---------- MOST DANGEROUS TRACK SECTION (new) ----------
st.markdown('<div class="section-header">⚠️ Most Dangerous Track Section</div>', unsafe_allow_html=True)

if most_dangerous is not None:
    d_color, d_label, d_emoji = section_status_color(most_dangerous["latest_risk_level"])
    st.markdown(f"""
    <div class="danger-highlight">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
        <div>
          <div style="font-size:13px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">Highest Average Risk</div>
          <div style="font-size:28px; font-weight:800; color:white;">📍 {most_dangerous['section']}</div>
        </div>
        <div style="display:flex; gap:32px; flex-wrap:wrap;">
          <div>
            <div style="font-size:12px; color:#64748b; text-transform:uppercase;">Avg Risk Score</div>
            <div style="font-size:22px; font-weight:700; color:#f87171;">{most_dangerous['avg_risk_score']}</div>
          </div>
          <div>
            <div style="font-size:12px; color:#64748b; text-transform:uppercase;">Defects</div>
            <div style="font-size:22px; font-weight:700; color:#fb923c;">{most_dangerous['defect_count']}</div>
          </div>
          <div>
            <div style="font-size:12px; color:#64748b; text-transform:uppercase;">Latest Risk Level</div>
            <div style="font-size:22px; font-weight:700; color:{d_color};">{d_emoji} {d_label}</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Not enough section data yet to determine the most dangerous track section.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- INFRASTRUCTURE HEALTH KPI (new) ----------
st.markdown('<div class="section-header">🏥 Infrastructure Health</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="glass-card">
  <div class="glass-card-label">Infrastructure Health Score</div>
  <div class="glass-card-value" style="color:{health_status_color};">{health_score}%</div>
  <div class="glass-card-sub">
    <div class="glass-card-sub-item">Health Status<strong style="color:{health_status_color};">{health_status}</strong></div>
    <div class="glass-card-sub-item">Health Trend<strong style="color:{health_trend_color};">{health_trend}</strong></div>
    <div class="glass-card-sub-item">Critical Alerts<strong style="color:#f87171;">{critical_alert_count}</strong></div>
    <div class="glass-card-sub-item">Avg Risk Score<strong style="color:#e2e8f0;">{avg_risk_score if total_events > 0 else 'N/A'}</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- RISK DISTRIBUTION ANALYTICS (new) ----------
st.markdown('<div class="section-header">📉 Risk Distribution Analytics</div>', unsafe_allow_html=True)

if not df.empty and "RiskLevel" in df.columns and df["RiskLevel"].notna().any():
    level_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    counts = df["RiskLevel"].astype(str).str.strip().str.upper().value_counts()
    chart_data = pd.DataFrame({
        "RiskLevel": level_order,
        "Count": [int(counts.get(lvl, 0)) for lvl in level_order]
    }).set_index("RiskLevel")
    st.bar_chart(chart_data, use_container_width=True)
else:
    st.info("No RiskLevel data found in detection_history.csv yet.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- OBSTACLE INTELLIGENCE PANEL (new) ----------
st.markdown('<div class="section-header">🛑 Obstacle Intelligence Panel</div>', unsafe_allow_html=True)

if obstacle_stats is not None:
    o1, o2, o3 = st.columns(3)
    with o1:
        st.markdown(f"""
        <div class="obstacle-card">
          <div class="obstacle-value">{obstacle_stats['total_events']}</div>
          <div class="obstacle-label">Total Obstacle Events</div>
        </div>
        """, unsafe_allow_html=True)
    with o2:
        st.markdown(f"""
        <div class="obstacle-card">
          <div class="obstacle-value">{obstacle_stats['most_common']}</div>
          <div class="obstacle-label">Most Common Obstacle</div>
        </div>
        """, unsafe_allow_html=True)
    with o3:
        st.markdown(f"""
        <div class="obstacle-card">
          <div class="obstacle-value">{obstacle_stats['total_obstacle_count']}</div>
          <div class="obstacle-label">Total Obstacles Logged</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No obstacle events recorded yet.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- RISK PANEL + SYSTEM HEALTH ----------
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-header">🚨 Executive Risk Summary</div>', unsafe_allow_html=True)

    risk_score_display = avg_risk_score if total_events > 0 else "N/A"

    if risk_level == "HIGH":
        st.error(f"""
**{risk_level_icon} Infrastructure Risk Level: HIGH**

Average Risk Score: **{risk_score_display}** / 100  
Defects Detected: **{defects}** &nbsp;({defect_pct}% of {total_events} events)

**Recommended Action:**  
⚠️ Immediate inspection required on flagged track segments.
""")
    elif risk_level == "MEDIUM":
        st.warning(f"""
**{risk_level_icon} Infrastructure Risk Level: MEDIUM**

Average Risk Score: **{risk_score_display}** / 100  
Defects Detected: **{defects}** &nbsp;({defect_pct}% of {total_events} events)

**Recommended Action:**  
🔍 Schedule a targeted inspection within 24–48 hours.
""")
    else:
        st.success(f"""
**{risk_level_icon} Infrastructure Risk Level: LOW**

Average Risk Score: **{risk_score_display}** / 100  
Defects Detected: **{defects}** &nbsp;({defect_pct}% of {total_events} events)

**Recommended Action:**  
✅ Continue routine monitoring — all systems nominal.
""")

with right:
    st.markdown("""
<div class="health-box">
  <div class="section-header" style="margin-bottom:14px;">🟢 System Health</div>

  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">Detection Engine</div>
    <div class="health-status">ACTIVE</div>
  </div>
  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">Analytics Module</div>
    <div class="health-status">ACTIVE</div>
  </div>
  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">Alert Center</div>
    <div class="health-status">ACTIVE</div>
  </div>
  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">Database</div>
    <div class="health-status">CONNECTED</div>
  </div>
  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">YOLO Inference</div>
    <div class="health-status">READY</div>
  </div>
  <div class="health-row">
    <div class="health-dot"></div>
    <div class="health-label">Report Engine</div>
    <div class="health-status">ACTIVE</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- ALERT FEED ----------
st.markdown('<div class="section-header">📡 Recent Alert Feed</div>', unsafe_allow_html=True)

if not df.empty:
    latest = df.tail(5).iloc[::-1]  # most recent first
    for _, row in latest.iterrows():
        time_val = row.get("Time", "—")
        conf_val = row.get("Confidence", "—")
        risk_val = row.get("RiskScore", None)
        risk_str = f" | Risk: {risk_val}" if risk_val is not None else ""

        if row["Class"] == "defective":
            st.markdown(f"""
<div class="alert-card alert-defect">
  <span>🚨</span>
  <span><strong>DEFECT DETECTED</strong> &nbsp;|&nbsp; Confidence: {conf_val}{risk_str}</span>
  <span class="alert-meta">{time_val}</span>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="alert-card alert-safe">
  <span>✅</span>
  <span><strong>SAFE TRACK</strong> &nbsp;|&nbsp; Confidence: {conf_val}{risk_str}</span>
  <span class="alert-meta">{time_val}</span>
</div>
""", unsafe_allow_html=True)
else:
    st.info("No alerts generated yet. Run a detection to populate the feed.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- RECENT DETECTION RECORDS ----------
st.markdown('<div class="section-header">📊 Recent Detection Records</div>', unsafe_allow_html=True)

if not df.empty:
    recent_records = df.tail(10).iloc[::-1].reset_index(drop=True)
    recent_records.index += 1  # 1-based row numbers

    st.dataframe(recent_records, use_container_width=True)
else:
    st.info("No detection records found. Run a detection to generate data.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------- SYSTEM STATISTICS ----------
st.markdown('<div class="section-header">📈 System Statistics</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"""
<div class="health-box">
  <div style="font-size:15px; font-weight:700; color:#94a3b8; margin-bottom:14px; text-transform:uppercase; letter-spacing:0.8px;">Detection Summary</div>

  <div class="stat-row">
    <span class="stat-key">Total Events Logged</span>
    <span class="stat-val">{total_events}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Defects Detected</span>
    <span class="stat-val" style="color:#f87171;">{defects}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Safe Tracks Confirmed</span>
    <span class="stat-val" style="color:#4ade80;">{safe_tracks}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Defect Percentage</span>
    <span class="stat-val" style="color:{'#f87171' if defect_pct > 0 else '#4ade80'};">{defect_pct}%</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Safe Percentage</span>
    <span class="stat-val" style="color:#4ade80;">{safe_pct}%</span>
  </div>

</div>
""", unsafe_allow_html=True)

with col_b:
    # Detect if confidence is stored as decimal (e.g. 0.91) or percentage (e.g. 91.0)
    # Values <= 1.0 are treated as decimals and multiplied by 100 for display
    if avg_confidence > 0:
        if avg_confidence <= 1.0:
            conf_display = f"{avg_confidence * 100:.1f}%"
        else:
            conf_display = f"{avg_confidence:.1f}%"
    else:
        conf_display = "N/A"
    risk_display_stat = str(avg_risk_score) if total_events > 0 else "N/A"

    st.markdown(f"""
<div class="health-box">
  <div style="font-size:15px; font-weight:700; color:#94a3b8; margin-bottom:14px; text-transform:uppercase; letter-spacing:0.8px;">Performance Metrics</div>

  <div class="stat-row">
    <span class="stat-key">Average Confidence</span>
    <span class="stat-val" style="color:#4ade80;">{conf_display}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Average Risk Score</span>
    <span class="stat-val" style="color:{risk_level_color};">{risk_display_stat}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Risk Level</span>
    <span class="stat-val" style="color:{risk_level_color};">{risk_level_icon} {risk_level}</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">YOLO Model Status</span>
    <span class="stat-val" style="color:#4ade80;">ACTIVE</span>
  </div>
  <div class="stat-row">
    <span class="stat-key">Database Status</span>
    <span class="stat-val" style="color:#4ade80;">CONNECTED</span>
  </div>

</div>
""", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#334155; font-size:12px; padding-bottom:20px;">
  TrackGuard AI &nbsp;•&nbsp; Railway Infrastructure Intelligence Platform &nbsp;•&nbsp; Powered by YOLO + Streamlit
</div>
""", unsafe_allow_html=True)