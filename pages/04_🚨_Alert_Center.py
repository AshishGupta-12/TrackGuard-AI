import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Alert Center",
    page_icon="🚨",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Premium "Command Center" styling (visual only — no data/business logic)
# ---------------------------------------------------------------------------
st.markdown("""
<style>

/* ---------- Header / hero ---------- */
.ops-header {
    background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.95) 100%);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.ops-header-eyebrow {
    color: #38bdf8;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.ops-header-title {
    color: #f8fafc;
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.2;
}
.ops-header-sub {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}
.ops-header-meta {
    display: flex;
    gap: 18px;
    margin-top: 14px;
    flex-wrap: wrap;
}
.ops-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(148,163,184,0.10);
    border: 1px solid rgba(148,163,184,0.20);
    color: #cbd5e1;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}
.ops-pill-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px #22c55e;
}

/* ---------- Section headers ---------- */
.section-title {
    color: #f1f5f9;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 6px 0 14px 0;
    padding-left: 10px;
    border-left: 4px solid #38bdf8;
}

/* ---------- KPI glass cards ---------- */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 14px;
    margin-bottom: 6px;
}
.kpi-card {
    position: relative;
    overflow: hidden;
    border-radius: 14px;
    padding: 18px 16px;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(148,163,184,0.16);
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
}
.kpi-card::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-critical::after { background: #ef4444; }
.kpi-high::after     { background: #f97316; }
.kpi-medium::after   { background: #eab308; }
.kpi-low::after       { background: #3b82f6; }
.kpi-safe::after      { background: #22c55e; }
.kpi-total::after     { background: #a78bfa; }

.kpi-icon { font-size: 1.3rem; margin-bottom: 6px; display: block; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #f8fafc; line-height: 1; }
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-top: 4px;
}

/* ---------- Severity badges ---------- */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
.badge-critical { background: rgba(239,68,68,0.18); color: #fca5a5; border: 1px solid rgba(239,68,68,0.45); }
.badge-high     { background: rgba(249,115,22,0.18); color: #fdba74; border: 1px solid rgba(249,115,22,0.45); }
.badge-medium   { background: rgba(234,179,8,0.18); color: #fde047; border: 1px solid rgba(234,179,8,0.45); }
.badge-low      { background: rgba(59,130,246,0.18); color: #93c5fd; border: 1px solid rgba(59,130,246,0.45); }
.badge-safe     { background: rgba(34,197,94,0.18); color: #86efac; border: 1px solid rgba(34,197,94,0.45); }

/* ---------- Alert feed cards ---------- */
.alert-card {
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 16px;
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(148,163,184,0.14);
    box-shadow: 0 4px 16px rgba(0,0,0,0.16);
}
.alert-card-critical { border-left: 5px solid #ef4444; }
.alert-card-high     { border-left: 5px solid #f97316; }
.alert-card-medium   { border-left: 5px solid #eab308; }
.alert-card-low      { border-left: 5px solid #3b82f6; }
.alert-card-safe     { border-left: 5px solid #22c55e; }

/* Premium incident styling for Critical / High */
.alert-card-incident {
    border-width: 1px;
    border-style: solid;
}
.alert-card-critical.alert-card-incident {
    background: linear-gradient(135deg, rgba(239,68,68,0.10) 0%, rgba(239,68,68,0.02) 100%);
    border-color: rgba(239,68,68,0.35);
    box-shadow: 0 4px 22px rgba(239,68,68,0.12);
}
.alert-card-high.alert-card-incident {
    background: linear-gradient(135deg, rgba(249,115,22,0.10) 0%, rgba(249,115,22,0.02) 100%);
    border-color: rgba(249,115,22,0.30);
    box-shadow: 0 4px 22px rgba(249,115,22,0.10);
}

.alert-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.alert-card-title {
    color: #f1f5f9;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
}
.alert-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 10px 18px;
    margin-top: 6px;
}
.alert-field-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 2px;
}
.alert-field-value {
    font-size: 0.92rem;
    color: #e2e8f0;
    font-weight: 600;
}
.alert-action {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(148,163,184,0.14);
    font-size: 0.88rem;
    color: #cbd5e1;
}
.alert-action b { color: #f1f5f9; }

/* ---------- Section-wise summary cards ---------- */
.section-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}
.section-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(148,163,184,0.16);
    border-radius: 12px;
    padding: 14px 20px;
    min-width: 100px;
    text-align: center;
    box-shadow: 0 3px 12px rgba(0,0,0,0.14);
}
.section-card-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    color: #94a3b8;
    text-transform: uppercase;
}
.section-card-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #f8fafc;
    margin-top: 4px;
}

.last-updated {
    font-size: 0.85rem;
    color: #94a3b8;
    margin: -4px 0 18px 0;
}

/* ---------- Explanatory / executive note text ---------- */
.exec-note {
    font-size: 0.86rem;
    color: #94a3b8;
    margin: -4px 0 16px 0;
    line-height: 1.5;
}
.exec-note b { color: #cbd5e1; }

/* ---------- Panel wrapper for timeline / section summary ---------- */
.panel {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.16);
}

/* ---------- Footer ---------- */
.ops-footer {
    text-align: center;
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    padding: 22px 0 8px 0;
    margin-top: 18px;
    border-top: 1px solid rgba(148,163,184,0.14);
}

@media (max-width: 1100px) {
    .kpi-row { grid-template-columns: repeat(3, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header (Railway Operations Command Center)
# ---------------------------------------------------------------------------
st.markdown("""
<div class="ops-header">
    <div class="ops-header-eyebrow">TrackGuard AI · Railway Operations</div>
    <h1 class="ops-header-title">🚨 TrackGuard AI Alert Center</h1>
    <p class="ops-header-sub">
        Real-Time Railway Risk Monitoring &amp; Incident Intelligence
    </p>
    <div class="ops-header-meta">
        <span class="ops-pill"><span class="ops-pill-dot"></span> Monitoring Active</span>
        <span class="ops-pill">📡 AI-Powered Risk Scoring</span>
    </div>
</div>
""", unsafe_allow_html=True)

log_file = "database/detection_history.csv"

# ---------------------------------------------------------------------------
# Empty / missing / malformed data handling
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = ["Class", "Confidence", "Time"]

if not os.path.exists(log_file):

    st.warning("No alerts available yet. The detection log file has not been created.")

else:

    df = pd.read_csv(log_file)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]

    if missing_cols:

        st.error(
            f"⚠️ The detection log is missing required column(s): "
            f"{', '.join(missing_cols)}. Cannot display alerts until the log "
            f"format is corrected."
        )

    elif len(df) == 0:

        st.info("No alerts available yet. The detection log is currently empty.")

    else:

        # ---------------------------------------------------------------
        # Last Updated Timestamp (real file modification time)
        # ---------------------------------------------------------------
        last_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
        st.markdown(
            f"<div class='last-updated'>🕒 Last updated: "
            f"{last_modified.strftime('%Y-%m-%d %H:%M:%S')}</div>",
            unsafe_allow_html=True
        )

        # ---------------------------------------------------------------
        # Existing summary calculations (logic preserved exactly)
        # ---------------------------------------------------------------
        total = len(df)
        safe = len(df[df["Class"] == "non-defective"])

        critical = len(
            df[(df["Class"] == "defective") &
               (df["Confidence"] >= 0.80)]
        )

        high = len(
            df[(df["Class"] == "defective") &
               (df["Confidence"] >= 0.60) &
               (df["Confidence"] < 0.80)]
        )

        medium = len(
            df[(df["Class"] == "defective") &
               (df["Confidence"] >= 0.40) &
               (df["Confidence"] < 0.60)]
        )

        low = len(
            df[(df["Class"] == "defective") &
               (df["Confidence"] < 0.40)]
        )

        # ---------------------------------------------------------------
        # Parse Time column for charting (rows that fail to parse are
        # simply excluded from the timeline only — feed is unaffected)
        # ---------------------------------------------------------------
        df_parsed = df.copy()
        df_parsed["_ParsedTime"] = pd.to_datetime(df_parsed["Time"], errors="coerce")

        def severity_label(row):
            if row["Class"] != "defective":
                return "Safe"
            c = row["Confidence"]
            if c >= 0.80:
                return "Critical"
            elif c >= 0.60:
                return "High"
            elif c >= 0.40:
                return "Medium"
            else:
                return "Low"

        df_parsed["_Severity"] = df_parsed.apply(severity_label, axis=1)

        tab_overview, tab_feed = st.tabs(["📊 Overview", "🚨 Alert Feed"])

        # =================================================================
        # OVERVIEW TAB
        # =================================================================
        with tab_overview:

            st.markdown('<div class="section-title">Alert Summary</div>', unsafe_allow_html=True)

            st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card kpi-total">
        <span class="kpi-icon">📊</span>
        <div class="kpi-value">{total}</div>
        <div class="kpi-label">Total Alerts</div>
    </div>
    <div class="kpi-card kpi-critical">
        <span class="kpi-icon">🚨</span>
        <div class="kpi-value">{critical}</div>
        <div class="kpi-label">Critical</div>
    </div>
    <div class="kpi-card kpi-high">
        <span class="kpi-icon">🟠</span>
        <div class="kpi-value">{high}</div>
        <div class="kpi-label">High</div>
    </div>
    <div class="kpi-card kpi-medium">
        <span class="kpi-icon">🟡</span>
        <div class="kpi-value">{medium}</div>
        <div class="kpi-label">Medium</div>
    </div>
    <div class="kpi-card kpi-low">
        <span class="kpi-icon">🔵</span>
        <div class="kpi-value">{low}</div>
        <div class="kpi-label">Low</div>
    </div>
    <div class="kpi-card kpi-safe">
        <span class="kpi-icon">✅</span>
        <div class="kpi-value">{safe}</div>
        <div class="kpi-label">Safe Events</div>
    </div>
</div>
""", unsafe_allow_html=True)

            st.divider()

            # -------------------------------------------------------
            # Section-wise Alert Summary (real data only)
            # -------------------------------------------------------
            st.markdown('<div class="section-title">Section-wise Alert Summary</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="exec-note">Aggregated alert counts grouped by track section, '
                'based on the current detection log.</div>',
                unsafe_allow_html=True
            )

            if "TrackSection" in df.columns:

                section_counts = (
                    df["TrackSection"]
                    .dropna()
                    .astype(str)
                    .value_counts()
                    .sort_index()
                )

                if len(section_counts) == 0:
                    st.info("No track section data found in the current log.")
                else:
                    cards_html = '<div class="panel"><div class="section-grid">'
                    for section_name, count in section_counts.items():
                        cards_html += (
                            f'<div class="section-card">'
                            f'<div class="section-card-label">{section_name}</div>'
                            f'<div class="section-card-value">{count}</div>'
                            f'</div>'
                        )
                    cards_html += "</div></div>"
                    st.markdown(cards_html, unsafe_allow_html=True)

            else:
                st.info("Track section data (`TrackSection`) is not available in the current log.")

            st.divider()

            # -------------------------------------------------------
            # Alert Timeline (real data only)
            # -------------------------------------------------------
            st.markdown('<div class="section-title">Alert Timeline</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="exec-note">Shows alert activity trends based on real detection history.</div>',
                unsafe_allow_html=True
            )

            timeline_df = df_parsed.dropna(subset=["_ParsedTime"])

            if len(timeline_df) == 0:
                st.info("No valid timestamps available to build a timeline.")
            else:
                timeline_df = timeline_df.copy()
                timeline_df["_Date"] = timeline_df["_ParsedTime"].dt.date

                timeline_grouped = (
                    timeline_df
                    .groupby(["_Date", "_Severity"])
                    .size()
                    .unstack(fill_value=0)
                    .sort_index()
                )

                severity_colors = {
                    "Critical": "#ef4444",
                    "High": "#f97316",
                    "Medium": "#eab308",
                    "Low": "#3b82f6",
                    "Safe": "#22c55e",
                }
                ordered_cols = [c for c in severity_colors if c in timeline_grouped.columns]
                timeline_grouped = timeline_grouped[ordered_cols]

                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.bar_chart(
                    timeline_grouped,
                    color=[severity_colors[c] for c in ordered_cols]
                )
                st.markdown('</div>', unsafe_allow_html=True)

        # =================================================================
        # ALERT FEED TAB
        # =================================================================
        with tab_feed:

            st.markdown('<div class="section-title">Latest Alert Feed</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="exec-note">Displays the latest incidents generated by the AI inspection system.</div>',
                unsafe_allow_html=True
            )

            latest = df.iloc[::-1]

            for _, row in latest.iterrows():

                confidence = float(row["Confidence"])
                section_value = row["TrackSection"] if "TrackSection" in df.columns and pd.notna(row.get("TrackSection")) else None

                if row["Class"] == "defective":

                    risk_score = min(
                        100,
                        int(confidence * 100 + 20)
                    )

                    if confidence >= 0.80:
                        card_class = "alert-card-critical"
                        badge_class = "badge-critical"
                        icon = "🔴"
                        title = "CRITICAL ALERT"
                        priority = "CRITICAL"
                        action = "Immediate inspection and maintenance required."
                        incident_class = "alert-card-incident"

                    elif confidence >= 0.60:
                        card_class = "alert-card-high"
                        badge_class = "badge-high"
                        icon = "🟠"
                        title = "HIGH RISK ALERT"
                        priority = "HIGH"
                        action = "Dispatch maintenance team as soon as possible."
                        incident_class = "alert-card-incident"

                    elif confidence >= 0.40:
                        card_class = "alert-card-medium"
                        badge_class = "badge-medium"
                        icon = "🟡"
                        title = "MEDIUM RISK ALERT"
                        priority = "MEDIUM"
                        action = "Schedule inspection within maintenance window."
                        incident_class = ""

                    else:
                        card_class = "alert-card-low"
                        badge_class = "badge-low"
                        icon = "🔵"
                        title = "LOW RISK ALERT"
                        priority = "LOW"
                        action = "Monitor and review future detections."
                        incident_class = ""

                    section_field = (
                        f'<div><div class="alert-field-label">Track Section</div>'
                        f'<div class="alert-field-value">{section_value}</div></div>'
                        if section_value is not None else ""
                    )

                    st.markdown(f"""
<div class="alert-card {card_class} {incident_class}">
    <div class="alert-card-header">
        <h4 class="alert-card-title">{icon} {title}</h4>
        <span class="badge {badge_class}">{priority}</span>
    </div>
    <div class="alert-card-grid">
        <div><div class="alert-field-label">Time</div><div class="alert-field-value">{row['Time']}</div></div>
        {section_field}
        <div><div class="alert-field-label">Issue</div><div class="alert-field-value">Railway Track Defect</div></div>
        <div><div class="alert-field-label">Confidence</div><div class="alert-field-value">{confidence:.2f}</div></div>
        <div><div class="alert-field-label">Risk Score</div><div class="alert-field-value">{risk_score}/100</div></div>
    </div>
    <div class="alert-action"><b>Recommended Action:</b> {action}</div>
</div>
""", unsafe_allow_html=True)

                else:

                    section_field = (
                        f'<div><div class="alert-field-label">Track Section</div>'
                        f'<div class="alert-field-value">{section_value}</div></div>'
                        if section_value is not None else ""
                    )

                    st.markdown(f"""
<div class="alert-card alert-card-safe">
    <div class="alert-card-header">
        <h4 class="alert-card-title">✅ SAFE TRACK STATUS</h4>
        <span class="badge badge-safe">SAFE</span>
    </div>
    <div class="alert-card-grid">
        <div><div class="alert-field-label">Time</div><div class="alert-field-value">{row['Time']}</div></div>
        {section_field}
        <div><div class="alert-field-label">Issue</div><div class="alert-field-value">No Critical Defect Detected</div></div>
        <div><div class="alert-field-label">Confidence</div><div class="alert-field-value">{confidence:.2f}</div></div>
    </div>
    <div class="alert-action"><b>Recommended Action:</b> Continue monitoring operations.</div>
</div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="ops-footer">TrackGuard AI · Railway Infrastructure Intelligence Platform</div>',
    unsafe_allow_html=True
)