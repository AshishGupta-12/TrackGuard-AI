import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Analytics", layout="wide")

# =============================================================
# PREMIUM DARK THEME / GLASS CARD STYLING
# (visual only — consistent with app.py / Dashboard / Alerts pages)
# =============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #11161f 0%, #0a0d13 60%, #060709 100%);
        color: #e6e9ef;
    }

    h1, h2, h3, h4 {
        color: #f2f4f8;
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: 0.3px;
    }

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
        font-size: 40px;
        font-weight: 800;
        color: white;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 16px;
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

    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #1e293b;
        color: #f2f4f8;
    }

    .glass-card {
        background: linear-gradient(145deg, #1E293B, #162032);
        border: 1px solid #334155;
        border-left: 4px solid #4ade80;
        border-radius: 18px;
        padding: 18px 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 18px rgba(0,0,0,0.35);
        margin-bottom: 14px;
        transition: border-color 0.2s, transform 0.2s;
    }
    .glass-card:hover { border-color: #4ade80; transform: translateY(-2px); }

    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
    }

    .info-box {
        background: rgba(255,255,255,0.03);
        border: 1px dashed rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 16px;
        color: #b7c0cc;
        text-align: center;
        font-size: 0.95rem;
    }

    .explain-box {
        background: rgba(148,163,184,0.06);
        border-left: 3px solid #4ade80;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: -4px;
        margin-bottom: 18px;
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #334155;
    }

    /* ── Glass panel wrapper for chart sections ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: linear-gradient(160deg, rgba(26,35,53,0.6), rgba(19,27,43,0.7));
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,0.18);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        padding: 6px 6px 2px 6px;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 28px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================
# HERO SECTION
# =============================================================
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">📊 TRACKGUARD AI ANALYTICS CENTER</div>
      <div class="hero-sub">Railway Infrastructure Intelligence &amp; Data Insights</div>
      <div class="hero-badge">🟢 System Online</div>
    </div>
    """,
    unsafe_allow_html=True,
)

log_file = "database/detection_history.csv"

# Plotly dark template helper, applied consistently below
PLOTLY_TEMPLATE = "plotly_dark"


def safe_columns_present(dataframe, columns):
    """Return list of columns that exist in dataframe."""
    return [c for c in columns if c in dataframe.columns]


def kpi_card(col, label, value):
    with col:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if os.path.exists(log_file):

    df = pd.read_csv(log_file)

    if df.empty:
        st.warning("Detection history file exists but contains no records yet.")
    else:

        # =====================================================
        # 1. EXECUTIVE ANALYTICS SECTION (real KPIs from CSV)
        # =====================================================
        st.markdown('<div class="section-header">🧭 Executive Summary</div>', unsafe_allow_html=True)

        total_inspections = len(df)

        total_defects = "N/A"
        if "Class" in df.columns:
            total_defects = int(df["Class"].notna().sum())

        avg_confidence = "N/A"
        if "Confidence" in df.columns and pd.to_numeric(df["Confidence"], errors="coerce").notna().any():
            avg_confidence = f'{pd.to_numeric(df["Confidence"], errors="coerce").mean():.2f}'

        avg_risk = "N/A"
        if "RiskScore" in df.columns and pd.to_numeric(df["RiskScore"], errors="coerce").notna().any():
            avg_risk = f'{pd.to_numeric(df["RiskScore"], errors="coerce").mean():.2f}'

        k1, k2, k3, k4 = st.columns(4)
        kpi_card(k1, "Total Inspections", total_inspections)
        kpi_card(k2, "Total Defects", total_defects)
        kpi_card(k3, "Average Confidence", avg_confidence)
        kpi_card(k4, "Average Risk Score", avg_risk)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # DETECTION HISTORY TABLE (existing — preserved)
        # =====================================================
        st.markdown('<div class="section-header">📋 Detection History</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.dataframe(df, use_container_width=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # DETECTION DISTRIBUTION PIE + DEFECT ANALYSIS BAR
        # (existing — preserved)
        # =====================================================
        if "Class" in df.columns:
            st.markdown('<div class="section-header">🧩 Detection Distribution</div>', unsafe_allow_html=True)

            class_counts = df["Class"].value_counts().reset_index()
            class_counts.columns = ["Class", "Count"]

            with st.container(border=True):
                c1, c2 = st.columns(2)

                with c1:
                    pie = px.pie(
                        class_counts,
                        names="Class",
                        values="Count",
                        title="Detection Distribution",
                        template=PLOTLY_TEMPLATE,
                    )
                    st.plotly_chart(pie, use_container_width=True)

                with c2:
                    bar = px.bar(
                        class_counts,
                        x="Class",
                        y="Count",
                        title="Defect Analysis",
                        template=PLOTLY_TEMPLATE,
                    )
                    st.plotly_chart(bar, use_container_width=True)
        else:
            st.markdown(
                '<div class="info-box">Column "Class" not found — Detection Distribution and Defect Analysis charts are unavailable.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 2. RISK TREND ANALYSIS (Time vs RiskScore)
        # =====================================================
        st.markdown('<div class="section-header">📈 Risk Trend Analysis</div>', unsafe_allow_html=True)

        if safe_columns_present(df, ["Time", "RiskScore"]) == ["Time", "RiskScore"]:
            trend_df = df.copy()
            trend_df["Time"] = pd.to_datetime(trend_df["Time"], errors="coerce")
            trend_df["RiskScore"] = pd.to_numeric(trend_df["RiskScore"], errors="coerce")
            trend_df = trend_df.dropna(subset=["Time", "RiskScore"]).sort_values("Time")

            if not trend_df.empty:
                with st.container(border=True):
                    risk_line = px.line(
                        trend_df,
                        x="Time",
                        y="RiskScore",
                        title="Risk Score Over Time",
                        template=PLOTLY_TEMPLATE,
                        markers=True,
                    )
                    st.plotly_chart(risk_line, use_container_width=True)
                st.markdown(
                    '<div class="explain-box">📌 This chart tracks how the risk score has evolved over time, '
                    'helping operations teams spot emerging trends and prioritize segments showing sustained increases in risk.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="info-box">No valid Time/RiskScore data available to plot the risk trend.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="info-box">Columns "Time" and/or "RiskScore" not found — Risk Trend Analysis unavailable.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 3. TRACK SECTION ANALYTICS (avg RiskScore per section)
        # =====================================================
        st.markdown('<div class="section-header">🛤️ Track Section Analytics</div>', unsafe_allow_html=True)

        if safe_columns_present(df, ["TrackSection", "RiskScore"]) == ["TrackSection", "RiskScore"]:
            section_df = df.copy()
            section_df["RiskScore"] = pd.to_numeric(section_df["RiskScore"], errors="coerce")
            section_avg = (
                section_df.dropna(subset=["RiskScore"])
                .groupby("TrackSection")["RiskScore"]
                .mean()
                .reset_index()
                .sort_values("RiskScore", ascending=False)
            )

            if not section_avg.empty:
                with st.container(border=True):
                    section_bar = px.bar(
                        section_avg,
                        x="TrackSection",
                        y="RiskScore",
                        title="Average Risk Score per Track Section",
                        template=PLOTLY_TEMPLATE,
                    )
                    st.plotly_chart(section_bar, use_container_width=True)
            else:
                st.markdown(
                    '<div class="info-box">No valid TrackSection/RiskScore data available.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="info-box">Columns "TrackSection" and/or "RiskScore" not found — Track Section Analytics unavailable.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 4. DEFECT DISTRIBUTION BY SECTION
        # =====================================================
        st.markdown('<div class="section-header">🚧 Defect Distribution by Section</div>', unsafe_allow_html=True)

        if safe_columns_present(df, ["TrackSection", "Class"]) == ["TrackSection", "Class"]:
            section_defects = (
                df.dropna(subset=["TrackSection", "Class"])
                .groupby(["TrackSection", "Class"])
                .size()
                .reset_index(name="Count")
            )

            if not section_defects.empty:
                with st.container(border=True):
                    section_defect_bar = px.bar(
                        section_defects,
                        x="TrackSection",
                        y="Count",
                        color="Class",
                        title="Defects by Track Section",
                        template=PLOTLY_TEMPLATE,
                        barmode="stack",
                    )
                    st.plotly_chart(section_defect_bar, use_container_width=True)
            else:
                st.markdown(
                    '<div class="info-box">No defect records available by section.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="info-box">Columns "TrackSection" and/or "Class" not found — Defect Distribution by Section unavailable.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 5. RISK LEVEL DISTRIBUTION (Low / Medium / High / Critical)
        # =====================================================
        st.markdown('<div class="section-header">🚦 Risk Level Distribution</div>', unsafe_allow_html=True)

        if "RiskLevel" in df.columns:
            risk_level_counts = df["RiskLevel"].value_counts().reset_index()
            risk_level_counts.columns = ["RiskLevel", "Count"]

            if not risk_level_counts.empty:
                with st.container(border=True):
                    risk_level_chart = px.pie(
                        risk_level_counts,
                        names="RiskLevel",
                        values="Count",
                        title="Risk Level Distribution",
                        template=PLOTLY_TEMPLATE,
                        color="RiskLevel",
                        color_discrete_map={
                            "Low": "#2ecc71",
                            "Medium": "#f1c40f",
                            "High": "#e67e22",
                            "Critical": "#e74c3c",
                        },
                    )
                    st.plotly_chart(risk_level_chart, use_container_width=True)
                st.markdown(
                    '<div class="explain-box">📌 This breakdown shows the proportion of inspections falling into each risk '
                    'category, giving leadership a quick read on overall network risk exposure.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="info-box">No RiskLevel records available.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="info-box">Column "RiskLevel" not found — Risk Level Distribution unavailable.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 6. OBSTACLE INTELLIGENCE
        # =====================================================
        st.markdown('<div class="section-header">🚜 Obstacle Intelligence</div>', unsafe_allow_html=True)

        has_obstacle_count = "ObstacleCount" in df.columns
        has_obstacle_types = "ObstacleTypes" in df.columns

        if not has_obstacle_count and not has_obstacle_types:
            st.markdown(
                '<div class="info-box">No obstacle events recorded yet.</div>',
                unsafe_allow_html=True,
            )
        else:
            obstacle_total = 0
            most_common_obstacle = "N/A"

            if has_obstacle_count:
                numeric_obstacle_count = pd.to_numeric(df["ObstacleCount"], errors="coerce").fillna(0)
                obstacle_total = int(numeric_obstacle_count.sum())

            obstacle_type_counts = pd.DataFrame()
            if has_obstacle_types:
                # ObstacleTypes may contain comma-separated values per row
                exploded = (
                    df["ObstacleTypes"]
                    .dropna()
                    .astype(str)
                    .str.split(",")
                    .explode()
                    .str.strip()
                )
                exploded = exploded[exploded != ""]
                if not exploded.empty:
                    obstacle_type_counts = exploded.value_counts().reset_index()
                    obstacle_type_counts.columns = ["ObstacleType", "Count"]
                    most_common_obstacle = obstacle_type_counts.iloc[0]["ObstacleType"]

            if obstacle_total == 0 and obstacle_type_counts.empty:
                st.markdown(
                    '<div class="info-box">No obstacle events recorded yet.</div>',
                    unsafe_allow_html=True,
                )
            else:
                o1, o2 = st.columns(2)
                kpi_card(o1, "Total Obstacle Events", obstacle_total)
                kpi_card(o2, "Most Common Obstacle Type", most_common_obstacle)

                if not obstacle_type_counts.empty:
                    with st.container(border=True):
                        obstacle_chart = px.bar(
                            obstacle_type_counts,
                            x="ObstacleType",
                            y="Count",
                            title="Obstacle Frequency",
                            template=PLOTLY_TEMPLATE,
                        )
                        st.plotly_chart(obstacle_chart, use_container_width=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # =====================================================
        # 7. CONFIDENCE ANALYTICS
        # =====================================================
        st.markdown('<div class="section-header">🎯 Confidence Analytics</div>', unsafe_allow_html=True)

        if "Confidence" in df.columns:
            confidence_series = pd.to_numeric(df["Confidence"], errors="coerce").dropna()

            if not confidence_series.empty:
                with st.container(border=True):
                    conf_col1, conf_col2 = st.columns([1, 2])
                    kpi_card(conf_col1, "Average Confidence", f"{confidence_series.mean():.2f}")

                    with conf_col2:
                        confidence_hist = px.histogram(
                            confidence_series,
                            x=confidence_series,
                            nbins=20,
                            title="Confidence Distribution",
                            template=PLOTLY_TEMPLATE,
                            labels={"x": "Confidence"},
                        )
                        st.plotly_chart(confidence_hist, use_container_width=True)
                st.markdown(
                    '<div class="explain-box">📌 Model confidence reflects how certain the detection engine is in its '
                    'classifications. Consistently high confidence supports trust in automated defect flags, while a wider '
                    'spread may warrant manual review of borderline cases.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="info-box">No valid Confidence data available.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="info-box">Column "Confidence" not found — Confidence Analytics unavailable.</div>',
                unsafe_allow_html=True,
            )

        # =====================================================
        # FOOTER
        # =====================================================
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center; color:#334155; font-size:12px; padding-bottom:20px;">
              TrackGuard AI &nbsp;•&nbsp; Railway Infrastructure Intelligence Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    st.warning("No detection history available yet.")