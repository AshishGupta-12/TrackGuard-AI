# pages/model_performance.py — TrackGuard AI | Model Performance Center
# ====================================================================
# Standalone page. Does not import from or modify detection.py,
# dashboard.py, analytics.py, alerts.py, or app.py.
#
# Displays REAL training/evaluation artifacts from runs/detect/train-2/
# and the model's REAL reported metrics. No synthetic metrics, no
# placeholder images. Any missing artifact is shown as a graceful
# warning rather than an error or a fake substitute.

import os

import streamlit as st

# ════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ════════════════════════════════════════════════════════════════════
RUN_DIR = os.path.join("runs", "detect", "train-2")

# Real, reported evaluation metrics for this training run.
# Do not edit these without re-running evaluation — this page never
# computes or estimates metrics on its own.
METRICS = [
    ("Precision", 64.8, "#3B9EFF"),
    ("Recall", 69.7, "#30D158"),
    ("mAP50", 70.3, "#FFD60A"),
    ("mAP50-95", 45.2, "#FF9500"),
]

# (filename, display title, short description)
TRAINING_CHART = ("results.png", "Training Results",
                   "Loss curves, precision/recall, and mAP tracked across training epochs.")

CONFUSION_CHARTS = [
    ("confusion_matrix.png", "Confusion Matrix",
     "Raw class-wise prediction counts on the validation set."),
    ("confusion_matrix_normalized.png", "Confusion Matrix (Normalized)",
     "Class-wise prediction rates, normalized by true class."),
]

CURVE_CHARTS = [
    ("BoxF1_curve.png", "F1 Curve", "F1 score across confidence thresholds."),
    ("BoxPR_curve.png", "Precision–Recall Curve", "Precision vs. recall trade-off across thresholds."),
    ("BoxP_curve.png", "Precision Curve", "Precision across confidence thresholds."),
    ("BoxR_curve.png", "Recall Curve", "Recall across confidence thresholds."),
]


# ════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TrackGuard AI — Model Performance",
    page_icon="📊",
    layout="wide",
)


# ════════════════════════════════════════════════════════════════════
#  STYLING (own namespace: mpc-* — does not touch other pages' CSS)
# ════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #11161f 0%, #0a0d13 60%, #060709 100%);
        color: #e6e9ef;
    }

    .mpc-header {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2a1e 100%);
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .mpc-eyebrow {
        color: #38bdf8;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .mpc-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    .mpc-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .mpc-badge {
        display: inline-block;
        margin-top: 14px;
        padding: 5px 14px;
        border-radius: 999px;
        background: rgba(34,197,94,0.12);
        color: #4ade80;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 1px solid rgba(74,222,128,0.35);
    }

    .mpc-metric-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px 18px;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0,0,0,0.3);
        transition: border-color 0.2s;
        height: 100%;
    }
    .mpc-metric-card:hover { border-color: var(--accent, #38bdf8); }
    .mpc-metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .mpc-metric-label {
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 8px;
    }

    .mpc-section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 1.9rem 0 0.7rem 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #1e293b;
    }
    .mpc-section-title span {
        color: #38bdf8;
    }
    .mpc-chart-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 2px;
    }
    .mpc-chart-caption {
        color: #64748b;
        font-size: 0.82rem;
        margin-bottom: 10px;
    }
    .mpc-chart-frame {
        background: #0d1320;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 18px;
    }

    .mpc-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 26px 0;
    }

    .mpc-footer {
        text-align: center;
        color: #334155;
        font-size: 12px;
        padding-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════════
st.markdown(
    f"""
    <div class="mpc-header">
        <div class="mpc-eyebrow">TrackGuard AI &nbsp;•&nbsp; Model Intelligence</div>
        <div class="mpc-title">📊 Model Performance Center</div>
        <div class="mpc-subtitle">
            Evaluation metrics and training artifacts for the defect-detection model,
            sourced directly from <code>{RUN_DIR}</code>.
        </div>
        <div class="mpc-badge">● Reporting real evaluation artifacts — no synthetic data</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════
#  KEY METRICS
# ════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="mpc-section-title"><span>◆</span> Key Evaluation Metrics</div>',
    unsafe_allow_html=True,
)

cols = st.columns(len(METRICS))
for col, (label, value, color) in zip(cols, METRICS):
    with col:
        st.markdown(
            f"""
            <div class="mpc-metric-card" style="--accent:{color};">
                <div class="mpc-metric-value" style="color:{color};">{value:.1f}%</div>
                <div class="mpc-metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "Metrics above are taken directly from the train-2 evaluation run. "
    "This page does not recalculate, estimate, or fabricate any performance values."
)

st.markdown('<div class="mpc-divider"></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
#  ARTIFACT RENDERING HELPERS
# ════════════════════════════════════════════════════════════════════
def render_artifact(filename: str, title: str, caption: str) -> None:
    """Render a single artifact image if present; otherwise show a
    graceful warning. Never substitutes a placeholder image."""
    path = os.path.join(RUN_DIR, filename)

    st.markdown(f'<div class="mpc-chart-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mpc-chart-caption">{caption}</div>', unsafe_allow_html=True)

    if os.path.isfile(path):
        st.markdown('<div class="mpc-chart-frame">', unsafe_allow_html=True)
        st.image(path, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning(
            f"⚠️ **{filename}** was not found in `{RUN_DIR}`. "
            "This chart will display automatically once the artifact is generated — "
            "no placeholder is shown in its place."
        )


# ════════════════════════════════════════════════════════════════════
#  ARTIFACTS
# ════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="mpc-section-title"><span>◆</span> Training &amp; Evaluation Artifacts</div>',
    unsafe_allow_html=True,
)

if not os.path.isdir(RUN_DIR):
    st.error(
        f"❌ Run directory `{RUN_DIR}` was not found. "
        "Confirm that training has completed and that this path is correct "
        "relative to the app's working directory."
    )
else:
    # ── Training results (full width) ──────────────────────────────
    render_artifact(*TRAINING_CHART)

    # ── Confusion matrices (side by side) ──────────────────────────
    cm_cols = st.columns(2)
    for col, chart in zip(cm_cols, CONFUSION_CHARTS):
        with col:
            render_artifact(*chart)

    # ── Precision / Recall / F1 / PR curves (2x2 grid) ─────────────
    for i in range(0, len(CURVE_CHARTS), 2):
        row = st.columns(2)
        for col, chart in zip(row, CURVE_CHARTS[i:i + 2]):
            with col:
                render_artifact(*chart)


# ════════════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="mpc-divider"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="mpc-footer">
        TrackGuard AI &nbsp;•&nbsp; Model Performance Center &nbsp;•&nbsp;
        Artifacts sourced from runs/detect/train-2/
    </div>
    """,
    unsafe_allow_html=True,
)