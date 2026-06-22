# detection.py — TrackGuard AI | Railway Operations Command Center
# ====================================================================
# Real ML inference with YOLOv8 (defect + obstacle models).
# All detection, logging, risk scoring, and PDF reporting is live —
# no mock data, no placeholders, no random values.

import os
import tempfile
from datetime import datetime, timedelta

import cv2
import pandas as pd
import streamlit as st
from PIL import Image
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as PDFImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from ultralytics import YOLO

# ════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ════════════════════════════════════════════════════════════════════
DB_DIR = "database"
LOG_FILE = os.path.join(DB_DIR, "detection_history.csv")
DETECTION_IMG = os.path.join(DB_DIR, "latest_detection.jpg")
DETECTION_IMG_VIDEO = os.path.join(DB_DIR, "latest_detection_video.jpg")
PDF_REPORT = os.path.join(DB_DIR, "trackguard_report.pdf")
DEFECT_MODEL_PATH = "models/best.pt"
OBSTACLE_MODEL_PATH = "yolov8n.pt"

VIDEO_FRAME_SKIP = 5
DEFECT_CONF_THRESHOLD = 0.50
OBSTACLE_CONF_THRESHOLD = 0.40

# Track sections this deployment monitors
TRACK_SECTIONS = ["A-17", "B-04", "C-09", "D-12"]

# Duplicate-detection protection window (seconds). A new detection on the
# same Track Section + Class within this window is treated as a repeat
# frame/click rather than a new event, and is not logged again.
DUPLICATE_WINDOW_SECONDS = 30

# Risk levels, ordered low → critical, with the score threshold that
# starts each band and the colour used throughout the UI / PDF.
RISK_LEVELS = [
    ("Low",      0,  "#30D158"),
    ("Medium",  35,  "#FFD60A"),
    ("High",    60,  "#FF9500"),
    ("Critical", 80, "#FF3B3B"),
]

# Obstacle classes (from COCO, as used by yolov8n.pt) treated as elevating
# risk because they represent a foreign-object / safety hazard on or near
# the track, as opposed to incidental background objects.
HIGH_RISK_OBSTACLE_CLASSES = {
    "person", "car", "truck", "bus", "motorcycle", "bicycle",
    "train", "cow", "horse", "sheep", "dog",
}

os.makedirs(DB_DIR, exist_ok=True)


def _score_to_level(score: int) -> str:
    """Map a 0-100 risk score to its risk level band using RISK_LEVELS
    thresholds. Shared by the live risk engine and by legacy-CSV backfill."""
    level = RISK_LEVELS[0][0]
    for name, threshold, _ in RISK_LEVELS:
        if score >= threshold:
            level = name
    return level


# ════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TrackGuard AI — Command Center",
    page_icon="🚆",
    layout="wide",
)


# ════════════════════════════════════════════════════════════════════
#  COMMAND CENTER CSS
# ════════════════════════════════════════════════════════════════════
def inject_command_center_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --tg-bg: #0B1220;
            --tg-bg-alt: #0E1729;
            --tg-panel: rgba(18, 27, 46, 0.72);
            --tg-panel-border: rgba(120, 160, 220, 0.16);
            --tg-steel: #3B9EFF;
            --tg-text: #E8EEF7;
            --tg-text-dim: #8FA1BD;
            --tg-low: #30D158;
            --tg-medium: #FFD60A;
            --tg-high: #FF9500;
            --tg-critical: #FF3B3B;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(59,158,255,0.10), transparent 45%),
                radial-gradient(circle at 85% 100%, rgba(255,149,0,0.06), transparent 40%),
                var(--tg-bg);
            color: var(--tg-text);
        }

        section[data-testid="stSidebar"] {
            background: var(--tg-bg-alt);
            border-right: 1px solid var(--tg-panel-border);
        }

        /* ── Command Center header ───────────────────────────────── */
        .tg-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 22px 28px;
            margin-bottom: 22px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(59,158,255,0.10), rgba(18,27,46,0.6));
            border: 1px solid var(--tg-panel-border);
        }
        .tg-header-title {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 1.55rem;
            letter-spacing: 0.02em;
            color: var(--tg-text);
            margin: 0;
        }
        .tg-header-title span { color: var(--tg-steel); }
        .tg-header-sub {
            color: var(--tg-text-dim);
            font-size: 0.85rem;
            margin-top: 2px;
        }
        .tg-status-pill {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            padding: 6px 14px;
            border-radius: 999px;
            background: rgba(48, 209, 88, 0.12);
            color: var(--tg-low);
            border: 1px solid rgba(48, 209, 88, 0.35);
        }

        /* ── Alert cards ──────────────────────────────────────────── */
        .tg-alert {
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 10px;
            border-left: 4px solid var(--tg-accent, var(--tg-steel));
            background: var(--tg-panel);
            backdrop-filter: blur(10px);
        }
        .tg-alert-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .tg-alert-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 999px;
            color: #0B1220;
        }
        .tg-alert-meta {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: var(--tg-text-dim);
        }
        .tg-alert-meta b { color: var(--tg-text); }

        /* ── Risk badge inline ────────────────────────────────────── */
        .tg-risk-badge {
            font-family: 'JetBrains Mono', monospace;
            display: inline-block;
            font-weight: 700;
            font-size: 0.78rem;
            padding: 4px 12px;
            border-radius: 999px;
            color: #0B1220;
        }

        /* Tighten default Streamlit spacing in our themed pages */
        div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_color(level: str) -> str:
    for name, _, color in RISK_LEVELS:
        if name == level:
            return color
    return "#8FA1BD"


# ════════════════════════════════════════════════════════════════════
#  MODEL LOADING (cached)
# ════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_models():
    defect_model = YOLO(DEFECT_MODEL_PATH)
    obstacle_model = YOLO(OBSTACLE_MODEL_PATH)
    return defect_model, obstacle_model


defect_model, obstacle_model = load_models()


# ════════════════════════════════════════════════════════════════════
#  ADVANCED RISK SCORING ENGINE
# ════════════════════════════════════════════════════════════════════
def compute_risk(
    detected_class: str,
    confidence: float,
    obstacle_count: int = 0,
    obstacle_types: str = "",
) -> tuple[int, str]:
    """
    Composite risk engine. Returns (risk_score 0-100, risk_level).

    Score is built from four real signals:
      • Defect class       — 'defective' contributes a high base risk,
                              any other class contributes a low base risk.
      • Confidence score    — scales the base contribution; a low-confidence
                              defect call is intentionally pulled toward the
                              uncertain middle band rather than scored as
                              confidently safe or confidently critical.
      • Obstacle count      — each detected obstacle adds incremental risk,
                              capped so a single frame full of background
                              objects can't dominate the score.
      • Obstacle types      — obstacles in HIGH_RISK_OBSTACLE_CLASSES
                              (people, vehicles, animals) add more risk per
                              instance than incidental object classes.
    """
    # ── Defect contribution (0-70) ──────────────────────────────────
    if confidence < DEFECT_CONF_THRESHOLD:
        # Low-confidence calls land in the uncertain middle regardless
        # of predicted class — we don't trust the class label yet.
        defect_component = 38.0
    elif detected_class == "defective":
        defect_component = 40.0 + confidence * 30.0          # 40 → 70
    else:
        defect_component = confidence * 12.0                 # 0 → 12 (safe)

    # ── Obstacle contribution (0-30) ─────────────────────────────────
    types_list = [t.strip() for t in obstacle_types.split(",") if t.strip()]
    high_risk_hits = sum(1 for t in types_list if t in HIGH_RISK_OBSTACLE_CLASSES)
    low_risk_hits = max(0, obstacle_count - high_risk_hits)

    obstacle_component = min(30.0, high_risk_hits * 9.0 + low_risk_hits * 3.0)

    raw_score = defect_component + obstacle_component
    risk_score = int(round(min(100.0, max(0.0, raw_score))))
    risk_level = _score_to_level(risk_score)

    return risk_score, risk_level


def recommended_action(risk_level: str) -> str:
    return {
        "Low": "Continue routine monitoring. No immediate action required.",
        "Medium": "Schedule manual inspection within the next maintenance cycle.",
        "High": "Dispatch inspection team within 24 hours. Restrict speed if obstacles present.",
        "Critical": "Immediate inspection and maintenance required. Consider halting traffic on this section.",
    }.get(risk_level, "Manual review recommended.")

# ════════════════════════════════════════════════════════════════════
#  CSV LOGGING — with Track Section + duplicate protection
# ════════════════════════════════════════════════════════════════════
CSV_COLUMNS = [
    "Time", "TrackSection", "Class", "Confidence", "RiskScore", "RiskLevel",
    "ObstacleCount", "ObstacleTypes",
]


def _read_log() -> pd.DataFrame:
    """Read the CSV log, backfilling any columns missing from older files
    so the schema is always complete in memory."""
    df = pd.read_csv(LOG_FILE)
    for col in CSV_COLUMNS:
        if col not in df.columns:
            if col in ("ObstacleCount", "RiskScore"):
                df[col] = 0
            else:
                df[col] = ""
    df["ObstacleTypes"] = df["ObstacleTypes"].fillna("")
    df["TrackSection"] = df["TrackSection"].fillna("UNKNOWN")
    df["ObstacleCount"] = pd.to_numeric(df["ObstacleCount"], errors="coerce").fillna(0).astype(int)
    df["RiskScore"] = pd.to_numeric(df["RiskScore"], errors="coerce").fillna(0).astype(int)
    df["Confidence"] = pd.to_numeric(df["Confidence"], errors="coerce").fillna(0.0)
    # Legacy rows logged before RiskLevel existed: derive it from RiskScore
    # instead of defaulting to "Low", so old high-risk events still surface
    # correctly in Alert Center / Analytics.
    missing_level = df["RiskLevel"].isna() | (df["RiskLevel"].astype(str).str.strip() == "")
    if missing_level.any():
        df.loc[missing_level, "RiskLevel"] = df.loc[missing_level, "RiskScore"].apply(_score_to_level)
    return df


def is_duplicate_detection(track_section: str, class_name: str) -> bool:
    """True if an identical (section, class) detection was already logged
    within DUPLICATE_WINDOW_SECONDS. Keeps analytics clean when a user
    re-runs detection on the same frame or re-submits the same image."""
    if not os.path.exists(LOG_FILE):
        return False
    try:
        df = _read_log()
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return False
    if df.empty:
        return False

    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    cutoff = datetime.now() - timedelta(seconds=DUPLICATE_WINDOW_SECONDS)

    recent_matches = df[
        (df["TrackSection"] == track_section)
        & (df["Class"] == class_name)
        & (df["Time"] >= cutoff)
    ]
    return not recent_matches.empty


def log_detection(
    track_section: str,
    class_name: str,
    confidence: float,
    risk_score: int,
    risk_level: str,
    obstacle_count: int = 0,
    obstacle_types: str = "",
) -> bool:
    """Append one detection event to the CSV log.

    Returns True if the row was logged, False if it was suppressed as a
    duplicate (same Track Section + Class within DUPLICATE_WINDOW_SECONDS).
    """
    if is_duplicate_detection(track_section, class_name):
        return False

    new_row = pd.DataFrame([{
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "TrackSection": track_section,
        "Class": class_name,
        "Confidence": round(confidence, 4),
        "RiskScore": risk_score,
        "RiskLevel": risk_level,
        "ObstacleCount": obstacle_count,
        "ObstacleTypes": obstacle_types,
    }])

    if os.path.exists(LOG_FILE):
        existing = _read_log()
        updated = pd.concat([existing, new_row], ignore_index=True)
        updated.to_csv(LOG_FILE, index=False)
    else:
        new_row.to_csv(LOG_FILE, index=False)

    return True


# ════════════════════════════════════════════════════════════════════
#  PDF REPORT GENERATION
# ════════════════════════════════════════════════════════════════════
def create_pdf_report(
    track_section: str,
    detected_class: str,
    confidence: float,
    risk_score: int,
    risk_level: str,
    image_path: str,
    obstacle_count: int = 0,
    obstacle_types: str = "",
) -> str:
    doc = SimpleDocTemplate(PDF_REPORT, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    risk_style = ParagraphStyle(
        "RiskStyle", parent=styles["Normal"],
        textColor=rl_colors.HexColor(risk_color(risk_level)),
        fontSize=13, fontName="Helvetica-Bold",
    )
    content = []

    content.append(Paragraph("TrackGuard AI — Railway Inspection Report", styles["Title"]))
    content.append(Spacer(1, 8))
    content.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"],
    ))
    content.append(Spacer(1, 14))

    obs_display = obstacle_types if obstacle_types else "None detected"

    table_data = [
        ["Track Section", track_section],
        ["Detection Result", detected_class],
        ["Confidence", f"{confidence:.4f}"],
        ["Risk Score", f"{risk_score} / 100"],
        ["Risk Level", risk_level],
        ["Obstacle Count", str(obstacle_count)],
        ["Obstacle Types", obs_display],
        ["Recommended Action", recommended_action(risk_level)],
    ]
    tbl = Table(table_data, colWidths=[140, 330])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (1, 4), (1, 4), rl_colors.HexColor(risk_color(risk_level))),
        ("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, rl_colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    content.append(tbl)
    content.append(Spacer(1, 18))

    if os.path.exists(image_path):
        content.append(Paragraph("Detection Image", styles["Heading3"]))
        content.append(Spacer(1, 6))
        content.append(PDFImage(image_path, width=400, height=280))

    doc.build(content)
    return PDF_REPORT

inject_command_center_css()

st.markdown(
    """
    <div class="tg-header">
        <div>
            <div class="tg-header-title">🚆 TRACK<span>GUARD</span> AI</div>
            <div class="tg-header-sub">Railway Operations Command Center · Real-time YOLOv8 Inspection</div>
        </div>
        <div class="tg-status-pill">● SYSTEM ONLINE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
#  Detection Console
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("#### Inspection Console")
st.markdown(
    "Select the track section under inspection, then upload imagery or "
    "video for AI-powered defect analysis, risk assessment, and "
    "maintenance recommendations."
)

section_col, _ = st.columns([1, 2])
with section_col:
    track_section = st.selectbox("🛤 Track Section", TRACK_SECTIONS, index=0)

uploaded_file = st.file_uploader(
    "Upload Railway Media",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"],
)

if uploaded_file is None:
    st.info(
        "### 📤 Upload an Image or Video\n\n"
        "**Supported formats:** JPG · JPEG · PNG · MP4 · AVI · MOV\n\n"
        "The AI engine will automatically analyse the media for the "
        f"selected section (**{track_section}**) and generate:\n"
        "- Defect Detection\n- Risk Assessment\n- Alert Status\n- Maintenance Recommendation"
    )
    st.stop()

file_ext = uploaded_file.name.rsplit(".", 1)[-1].lower()

# ── IMAGE MODE ─────────────────────────────────────────────────────────────
if file_ext in {"jpg", "jpeg", "png"}:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📷 Original Image")
        st.image(image, use_container_width=True)

    # Write to a temp file so YOLO can read it from disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
        if image.mode != "RGB":
            image.convert("RGB").save(tmp_path)
        else:
            image.save(tmp_path)

    try:
        defect_results = defect_model(tmp_path, conf=DEFECT_CONF_THRESHOLD)
        obstacle_results = obstacle_model(tmp_path, conf=OBSTACLE_CONF_THRESHOLD)
    finally:
        os.unlink(tmp_path)   # clean up temp file

    # Annotated image: overlay both defect boxes and obstacle boxes
    annotated = defect_results[0].plot()
    for box in obstacle_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 100, 0), 2)
        cls_id = int(box.cls[0])
        label = obstacle_model.names[cls_id]
        cv2.putText(
            annotated, f"OBS:{label}", (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 100, 0), 2,
        )

    cv2.imwrite(DETECTION_IMG, annotated)

    with col2:
        st.subheader("🤖 AI Detection Result")
        st.image(annotated, channels="BGR", use_container_width=True)

    st.divider()

    # ── Obstacle summary ───────────────────────────────────────────────────
    obs_boxes = obstacle_results[0].boxes
    obs_names = [obstacle_model.names[int(b.cls[0])] for b in obs_boxes]
    obs_count = len(obs_names)
    obs_types_str = ",".join(obs_names)

    if obs_count > 0:
        st.warning(
            f"🚧 **{obs_count} obstacle(s) detected on or near track {track_section}:** "
            + ", ".join(obs_names)
        )

    # ── Defect analysis ────────────────────────────────────────────────────
    defect_boxes = defect_results[0].boxes

    if len(defect_boxes) == 0:
        st.success("✅ No defects detected by the defect model.")
        # Still log a clean "no defect" pass for this section, with any
        # obstacles found, so analytics reflect a complete inspection.
        risk_score, risk_level = compute_risk("non-defective", 1.0, obs_count, obs_types_str)
        logged = log_detection(
            track_section, "non-defective", 1.0, risk_score, risk_level,
            obstacle_count=obs_count, obstacle_types=obs_types_str,
        )
        if not logged:
            st.caption("⏱ Duplicate detection suppressed (same section/class within 30s).")
    else:
        st.warning(f"⚠ {len(defect_boxes)} defect detection(s) found")

        highest_conf = 0.0
        detected_class = ""

        for box in defect_boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = defect_model.names[cls_id]

            if conf > highest_conf:
                highest_conf = conf
                detected_class = class_name

            st.info(f"**Class:** {class_name} &nbsp;|&nbsp; **Confidence:** {conf:.4f}")

        risk_score, risk_level = compute_risk(
            detected_class, highest_conf, obs_count, obs_types_str
        )
        logged = log_detection(
            track_section, detected_class, highest_conf, risk_score, risk_level,
            obstacle_count=obs_count, obstacle_types=obs_types_str,
        )
        if not logged:
            st.caption("⏱ Duplicate detection suppressed (same section/class within 30s).")

        st.divider()

        # ── Risk display ───────────────────────────────────────────────────
        badge_color = risk_color(risk_level)
        st.markdown(
            f"""
            <div class="tg-alert" style="--tg-accent:{badge_color}; border-left-color:{badge_color};">
                <div class="tg-alert-top">
                    <span style="font-weight:700; font-size:1.05rem;">
                        Track {track_section} — {detected_class.upper()}
                    </span>
                    <span class="tg-alert-badge" style="background:{badge_color};">{risk_level}</span>
                </div>
                <div class="tg-alert-meta">
                    <b>Risk Score:</b> {risk_score}/100 &nbsp;|&nbsp;
                    <b>Confidence:</b> {highest_conf:.4f} &nbsp;|&nbsp;
                    <b>Obstacles:</b> {obs_count} ({obs_types_str if obs_types_str else 'none'})
                </div>
                <div class="tg-alert-meta" style="margin-top:6px;">
                    <b>Recommended Action:</b> {recommended_action(risk_level)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── PDF report ─────────────────────────────────────────────────────
        pdf_path = create_pdf_report(
            track_section, detected_class, highest_conf, risk_score, risk_level,
            DETECTION_IMG, obstacle_count=obs_count, obstacle_types=obs_types_str,
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Inspection Report (PDF)",
                data=f,
                file_name=f"trackguard_report_{track_section}.pdf",
                mime="application/pdf",
            )

# ── VIDEO MODE ─────────────────────────────────────────────────────────────
elif file_ext in {"mp4", "avi", "mov"}:
    st.subheader("🎥 Uploaded Video")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name

    st.video(video_path)

    st.info(f"Running defect detection on video frames for section {track_section}…")
    cap = cv2.VideoCapture(video_path)
    frame_placeholder = st.empty()
    status_text = st.empty()

    frame_idx = 0
    frames_processed = 0
    total_defects = 0
    highest_conf_video = 0.0
    detected_class_video = ""
    video_obs_count = 0
    video_obs_types: list = []

    # Track highest-confidence defect frame for PDF report (Feature 1)
    best_defect_frame = None          # annotated ndarray of peak-conf defect frame
    last_annotated_frame = None       # annotated ndarray of last processed frame

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_idx += 1
        if frame_idx % VIDEO_FRAME_SKIP != 0:
            continue

        frames_processed += 1
        results = defect_model(frame, conf=DEFECT_CONF_THRESHOLD)
        obs_results_frame = obstacle_model(frame, conf=OBSTACLE_CONF_THRESHOLD)
        annotated_frame = results[0].plot()

        for ob in obs_results_frame[0].boxes:
            ox1, oy1, ox2, oy2 = map(int, ob.xyxy[0])
            cv2.rectangle(annotated_frame, (ox1, oy1), (ox2, oy2), (255, 100, 0), 2)
            ob_label = obstacle_model.names[int(ob.cls[0])]
            cv2.putText(
                annotated_frame, f"OBS:{ob_label}", (ox1, max(oy1 - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 100, 0), 2,
            )
            video_obs_count += 1
            video_obs_types.append(ob_label)

        frame_placeholder.image(annotated_frame, channels="BGR", use_container_width=True)
        last_annotated_frame = annotated_frame  # keep reference to last processed frame

        for box in results[0].boxes:
            total_defects += 1
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = defect_model.names[cls_id]
            if conf > highest_conf_video:
                highest_conf_video = conf
                detected_class_video = class_name
                best_defect_frame = annotated_frame  # save highest-confidence defect frame

        status_text.caption(f"Processed frame {frame_idx} | Defect events so far: {total_defects}")

    cap.release()
    os.unlink(video_path)

    st.divider()

    seen: dict = {}
    for t in video_obs_types:
        seen[t] = seen.get(t, 0) + 1
    obs_types_video_str = ",".join(seen.keys())

    if total_defects > 0:
        # ── Defect video path ──────────────────────────────────────────────
        risk_score_video, risk_level_video = compute_risk(
            detected_class_video, highest_conf_video,
            video_obs_count, obs_types_video_str,
        )
        logged = log_detection(
            track_section, detected_class_video, highest_conf_video,
            risk_score_video, risk_level_video,
            obstacle_count=video_obs_count, obstacle_types=obs_types_video_str,
        )
        if not logged:
            st.caption("⏱ Duplicate detection suppressed (same section/class within 30s).")

        # ── Feature 2: Defect result card ──────────────────────────────────
        badge_color = risk_color(risk_level_video)
        st.markdown(
            f"""
            <div style="border-radius:14px; padding:22px 26px; margin-bottom:16px;
                        background:rgba(18,27,46,0.72); border:1px solid rgba(120,160,220,0.16);
                        border-left:4px solid {badge_color};">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
                    <span style="font-family:'JetBrains Mono',monospace; font-weight:700;
                                 font-size:1.1rem; color:#E8EEF7;">
                        🎥 Video Inspection Complete
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
                                 font-weight:700; letter-spacing:0.06em; padding:5px 14px;
                                 border-radius:999px; background:{badge_color}; color:#0B1220;">
                        {risk_level_video}
                    </span>
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#E8EEF7;">
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD; width:38%;">Track Section</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace;">{track_section}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Detected Class</td>
                        <td style="padding:7px 0; font-weight:600;">{detected_class_video.upper()}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Confidence</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace;">{highest_conf_video:.4f}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Risk Score</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace; font-weight:700; color:{badge_color};">{risk_score_video} / 100</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Risk Level</td>
                        <td style="padding:7px 0; font-weight:700; color:{badge_color};">{risk_level_video}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(120,160,220,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Obstacle Count</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace;">{video_obs_count} ({obs_types_video_str if obs_types_video_str else 'none'})</td>
                    </tr>
                    <tr>
                        <td style="padding:7px 0; color:#8FA1BD;">Recommended Action</td>
                        <td style="padding:7px 0;">{recommended_action(risk_level_video)}</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Feature 1: PDF report for defect video ─────────────────────────
        # Save annotated frame from the highest-confidence defect detection
        if best_defect_frame is not None:
            cv2.imwrite(DETECTION_IMG_VIDEO, best_defect_frame)
        pdf_path = create_pdf_report(
            track_section, detected_class_video, highest_conf_video,
            risk_score_video, risk_level_video,
            DETECTION_IMG_VIDEO,
            obstacle_count=video_obs_count, obstacle_types=obs_types_video_str,
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Inspection Report (PDF)",
                data=f,
                file_name=f"trackguard_report_{track_section}.pdf",
                mime="application/pdf",
            )

    else:
        # ── Non-defective / clear / obstacle-only path ─────────────────────
        # Mirror image mode's non-defective logging path (see the
        # `len(defect_boxes) == 0` branch above): still log a clean "no
        # defect" pass for this section, with any obstacles found, so
        # Dashboard / Analytics / Alerts reflect a completed video
        # inspection even when no defect ever crossed the confidence
        # threshold. Uses the same compute_risk/log_detection calls and
        # the same "non-defective" class label as image mode — no new
        # logging format introduced.
        risk_score_video, risk_level_video = compute_risk(
            "non-defective", 1.0, video_obs_count, obs_types_video_str
        )
        logged = log_detection(
            track_section, "non-defective", 1.0, risk_score_video, risk_level_video,
            obstacle_count=video_obs_count, obstacle_types=obs_types_video_str,
        )
        if not logged:
            st.caption("⏱ Duplicate detection suppressed (same section/class within 30s).")

        if video_obs_count > 0:
            st.warning(
                f"🚧 **{video_obs_count} obstacle event(s) detected on or near track "
                f"{track_section}:** " + ", ".join(seen.keys())
            )

        # ── Feature 2: Non-defective result card ──────────────────────────
        badge_color = risk_color(risk_level_video)
        st.markdown(
            f"""
            <div style="border-radius:14px; padding:22px 26px; margin-bottom:16px;
                        background:rgba(18,27,46,0.72); border:1px solid rgba(48,209,88,0.25);
                        border-left:4px solid #30D158;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
                    <span style="font-family:'JetBrains Mono',monospace; font-weight:700;
                                 font-size:1.1rem; color:#E8EEF7;">
                        🎥 Video Inspection Complete
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
                                 font-weight:700; letter-spacing:0.06em; padding:5px 14px;
                                 border-radius:999px; background:#30D158; color:#0B1220;">
                        NON-DEFECTIVE
                    </span>
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#E8EEF7;">
                    <tr style="border-bottom:1px solid rgba(48,209,88,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD; width:38%;">Track Section</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace;">{track_section}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(48,209,88,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Status</td>
                        <td style="padding:7px 0; font-weight:700; color:#30D158;">✅ NON-DEFECTIVE</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(48,209,88,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Risk Score</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace; font-weight:700; color:{badge_color};">{risk_score_video} / 100</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(48,209,88,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Risk Level</td>
                        <td style="padding:7px 0; font-weight:700; color:{badge_color};">{risk_level_video}</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(48,209,88,0.12);">
                        <td style="padding:7px 0; color:#8FA1BD;">Obstacle Count</td>
                        <td style="padding:7px 0; font-family:'JetBrains Mono',monospace;">{video_obs_count} ({obs_types_video_str if obs_types_video_str else 'none'})</td>
                    </tr>
                    <tr>
                        <td style="padding:7px 0; color:#8FA1BD;">Recommended Action</td>
                        <td style="padding:7px 0;">{recommended_action(risk_level_video)}</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Feature 1: PDF report for non-defective / clear / obstacle-only video
        # Use last processed annotated frame as the report image
        if last_annotated_frame is not None:
            cv2.imwrite(DETECTION_IMG_VIDEO, last_annotated_frame)
        pdf_path = create_pdf_report(
            track_section, "non-defective", 1.0,
            risk_score_video, risk_level_video,
            DETECTION_IMG_VIDEO,
            obstacle_count=video_obs_count, obstacle_types=obs_types_video_str,
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Inspection Report (PDF)",
                data=f,
                file_name=f"trackguard_report_{track_section}.pdf",
                mime="application/pdf",
            )

    # ── Feature 3: Inspection Summary Card ────────────────────────────────────
    st.markdown(
        f"""
        <div style="border-radius:14px; padding:20px 26px; margin-top:18px;
                    background:rgba(18,27,46,0.72); border:1px solid rgba(120,160,220,0.16);">
            <div style="font-family:'JetBrains Mono',monospace; font-weight:700;
                        font-size:0.95rem; color:#8FA1BD; letter-spacing:0.06em;
                        text-transform:uppercase; margin-bottom:16px;">
                📊 Inspection Summary
            </div>
            <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px;">
                <div style="background:rgba(59,158,255,0.07); border-radius:10px; padding:14px 16px;
                            border:1px solid rgba(59,158,255,0.15); text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                                font-weight:800; color:#3B9EFF;">{frames_processed}</div>
                    <div style="font-size:0.78rem; color:#8FA1BD; margin-top:4px;">Frames Processed</div>
                </div>
                <div style="background:rgba(255,59,59,0.07); border-radius:10px; padding:14px 16px;
                            border:1px solid rgba(255,59,59,0.15); text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                                font-weight:800; color:#FF3B3B;">{total_defects}</div>
                    <div style="font-size:0.78rem; color:#8FA1BD; margin-top:4px;">Defects Found</div>
                </div>
                <div style="background:rgba(255,149,0,0.07); border-radius:10px; padding:14px 16px;
                            border:1px solid rgba(255,149,0,0.15); text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                                font-weight:800; color:#FF9500;">{video_obs_count}</div>
                    <div style="font-size:0.78rem; color:#8FA1BD; margin-top:4px;">Obstacle Events</div>
                </div>
                <div style="background:rgba(18,27,46,0.5); border-radius:10px; padding:14px 16px;
                            border:1px solid rgba(120,160,220,0.16); text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem;
                                font-weight:800; color:{risk_color(risk_level_video)};">{risk_level_video}</div>
                    <div style="font-size:0.78rem; color:#8FA1BD; margin-top:4px;">Risk Level</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )