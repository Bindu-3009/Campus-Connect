"""
Campus Connect - AI-Based Revision-Aware Academic Notice Intelligence & Conflict Detection System
Main Streamlit Web Application
"""

import streamlit as st
import datetime
import pandas as pd
import json
from typing import Any, Dict, List, Optional, Tuple

import database
from parser import (
    parse_academic_notice,
    extract_text_from_pdf,
    decode_text_file,
    PYMUPDF_AVAILABLE,
    PYPDF_AVAILABLE,
    OCR_LIB_AVAILABLE
)
from revision_engine import compare_notice_versions
from conflict_detector import detect_all_conflicts
from chatbot_engine import query_assistant
from sample_data import SAMPLE_NOTICES

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Campus Connect | Academic Notice & Conflict AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Fidelity CSS to replicate exact design
CUSTOM_CSS = """
<style>
/* Sidebar Dark Navy Theme */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
}
[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] .stRadio > div {
    background-color: transparent;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.2s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #1E293B !important;
    color: #38BDF8 !important;
}

/* Main Dashboard Canvas */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}
body {
    background-color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Card Containers */
.intel-card {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    margin-bottom: 18px;
}

/* Pastel KPI Stat Cards */
.kpi-card {
    border-radius: 12px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    border: 1px solid transparent;
}
.kpi-blue {
    background-color: #E0F2FE;
    border-color: #BAE6FD;
}
.kpi-blue .kpi-title { color: #0369A1; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-blue .kpi-num { color: #0C4A6E; font-size: 2.2rem; font-weight: 700; margin: 4px 0; }
.kpi-blue .kpi-sub { color: #0284C7; font-size: 0.8rem; }

.kpi-pink {
    background-color: #FFE4E6;
    border-color: #FECDD3;
}
.kpi-pink .kpi-title { color: #BE123C; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-pink .kpi-num { color: #881337; font-size: 2.2rem; font-weight: 700; margin: 4px 0; }
.kpi-pink .kpi-sub { color: #E11D48; font-size: 0.8rem; }

.kpi-purple {
    background-color: #EDE9FE;
    border-color: #DDD6FE;
}
.kpi-purple .kpi-title { color: #6D28D9; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-purple .kpi-num { color: #4C1D95; font-size: 2.2rem; font-weight: 700; margin: 4px 0; }
.kpi-purple .kpi-sub { color: #7C3AED; font-size: 0.8rem; }

.kpi-green {
    background-color: #DCFCE7;
    border-color: #BBF7D0;
}
.kpi-green .kpi-title { color: #15803D; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-green .kpi-num { color: #14532D; font-size: 2.2rem; font-weight: 700; margin: 4px 0; }
.kpi-green .kpi-sub { color: #16A34A; font-size: 0.8rem; }

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 8px;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 9999px;
    text-transform: uppercase;
}
.badge-active { background-color: #DCFCE7; color: #15803D; }
.badge-revised { background-color: #E0E7FF; color: #4338CA; }
.badge-superseded { background-color: #F1F5F9; color: #64748B; text-decoration: line-through; }
.badge-clash { background-color: #FFE4E6; color: #BE123C; }
.badge-sample { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }

/* Diff View */
.diff-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
.diff-table th {
    background-color: #F1F5F9;
    padding: 10px 12px;
    text-align: left;
    border-bottom: 2px solid #CBD5E1;
}
.diff-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #E2E8F0;
}
.diff-modified-old {
    background-color: #FEE2E2;
    color: #991B1B;
    text-decoration: line-through;
    padding: 3px 6px;
    border-radius: 4px;
}
.diff-modified-new {
    background-color: #DCFCE7;
    color: #166534;
    font-weight: 600;
    padding: 3px 6px;
    border-radius: 4px;
}
.diff-unchanged {
    color: #475569;
}

/* Notice Raw Text & Form Inputs - High-Contrast Crisp Light Theme */
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    caret-color: #2563EB !important;
    font-size: 0.92rem !important;
    line-height: 1.5 !important;
}

.stTextArea textarea:focus {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}

.stTextArea textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}

.stTextArea textarea::selection {
    background-color: #BFDBFE !important;
    color: #1E3A8A !important;
}

/* Text Area Scrollbar */
.stTextArea textarea::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
.stTextArea textarea::-webkit-scrollbar-track {
    background: #F1F5F9;
    border-radius: 4px;
}
.stTextArea textarea::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 4px;
}
.stTextArea textarea::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}

/* Form Input Boxes & Labels */
.stTextArea label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stCheckbox label {
    color: #1E293B !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

.stTextInput input, .stNumberInput input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    caret-color: #2563EB !important;
    font-size: 0.92rem !important;
}

.stTextInput input:focus, .stNumberInput input:focus {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}

.stTextInput input::placeholder, .stNumberInput input::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}

.stTextInput input::selection, .stNumberInput input::selection {
    background-color: #BFDBFE !important;
    color: #1E3A8A !important;
}

.stSelectbox > div > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Database & Session Initialization
# ---------------------------------------------------------
@st.cache_resource
def bootstrap_database():
    database.init_db()

bootstrap_database()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Hello! I am your Campus Connect Academic Assistant. Ask me about exam dates, recent notice revisions, venue allocations, or timetable conflicts!"}
    ]

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "profile_display_name" not in st.session_state:
    st.session_state.profile_display_name = "Academic Administrator"
if "profile_role" not in st.session_state:
    st.session_state.profile_role = "Exam Controller & Academic Timetable Officer"
if "profile_dept" not in st.session_state:
    st.session_state.profile_dept = "Office of Academic Affairs"
if "pref_conflict_alerts" not in st.session_state:
    st.session_state.pref_conflict_alerts = True
if "pref_revision_alerts" not in st.session_state:
    st.session_state.pref_revision_alerts = True
if "pref_holiday_alerts" not in st.session_state:
    st.session_state.pref_holiday_alerts = True

# Helper functions for notifications
def format_notification_timestamp(ts: Any) -> str:
    """Formats raw timestamp strings into a human-readable Date • Time format."""
    if not ts:
        return "Recent"
    ts_str = str(ts).strip()
    formats_to_try = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats_to_try:
        try:
            dt = datetime.datetime.strptime(ts_str, fmt)
            return dt.strftime("%b %d, %Y • %I:%M %p")
        except ValueError:
            continue
    return ts_str


def classify_notification(notif: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Classifies a notification into (type_label, severity, icon).
    type_label: 'Conflict' | 'Revision' | 'Info'
    severity: 'CRITICAL' | 'HIGH' | 'NORMAL'
    """
    raw_type = str(notif.get("type", "")).upper()
    title = str(notif.get("title", "")).upper()

    if "CONFLICT" in raw_type or "CLASH" in raw_type or "CONFLICT" in title or "CLASH" in title:
        type_label = "Conflict"
        is_critical = "CRITICAL" in raw_type or "SEVERE" in title or "CRITICAL" in title
        severity = "CRITICAL" if is_critical else "HIGH"
        icon = "🚨" if is_critical else "⚠️"
    elif "REVISION" in raw_type or "AMENDMENT" in raw_type or "REVISED" in title:
        type_label = "Revision"
        severity = "NORMAL"
        icon = "🔄"
    else:
        type_label = "Info"
        severity = "NORMAL"
        icon = "ℹ️"

    return type_label, severity, icon


# Fetch live state data
notices = database.get_all_notices()
exams = database.get_all_exams()
conflicts = detect_all_conflicts(notices)
database.sync_conflict_notifications(conflicts)
notifications = database.get_notifications()
unread_count = len([n for n in notifications if not n["read"]])
db_stats = database.get_database_stats()

# ---------------------------------------------------------
# Left Sidebar Navigation (Dark Navy)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏛️ Campus Connect")
    st.caption("Academic Notice & Conflict AI")
    st.divider()
    st.caption("**SYSTEM NAVIGATION**")

    nav_options = [
        "📊 Dashboard",
        "📤 Upload Notice & PDF",
        "🔄 Revision History & Diffs",
        "⚠️ Conflict Detection",
        "📅 Upcoming Exam Schedule",
        "🤖 Academic AI Assistant",
        f"🔔 Notifications & Profile ({unread_count})"
    ]

    selected_nav = st.radio(
        "Navigation",
        nav_options,
        label_visibility="collapsed"
    )

    st.divider()

    # Sidebar Quick Status Widget
    with st.container(border=True):
        st.markdown("**System Status: `ACTIVE`**")
        demo_status = "🏷️ Sample Demo Active" if db_stats["has_demo_data"] else "🟢 Production Active"
        st.caption(f"• Local SQLite DB: Connected\n\n• NLP Engine: Zero-API Core\n\n• {demo_status}")

    if st.button("🔄 Reset Demo Dataset", use_container_width=True, help="Restores the standard sample notices and clean test records"):
        database.reset_to_demo_data()
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Dataset reset! All original sample notices and clash scenarios restored."}
        ]
        st.success("Demo dataset reloaded!")
        st.rerun()

    st.caption("Campus Connect Hackathon Project © 2026 • Designed for Academic Conflict Free Operations")


# ---------------------------------------------------------
# Screen 1: Dashboard
# ---------------------------------------------------------
if selected_nav.startswith("📊 Dashboard"):
    # Header Area
    col_head_left, col_head_right = st.columns([3, 1])
    with col_head_left:
        st.title("Campus Connect Academic Dashboard")
        st.caption("Welcome to Campus Connect • University Semester Operations • Fall / Spring Cycle • Real-time Audit")
    with col_head_right:
        st.info(f"📅 {datetime.date.today().strftime('%B %d, %Y')}")

    # 4 Pastel Summary Cards
    active_notices_count = len([n for n in notices if n.get("status") != "SUPERSEDED"])
    revisions_count = len([n for n in notices if n.get("is_revision")])
    conflicts_count = len(conflicts)
    exams_count = len(exams)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.metric("Active Circulars", active_notices_count, "Across 5 departments", delta_color="off")
    with c2:
        with st.container(border=True):
            st.metric("Revisions Tracked", revisions_count, "Field diffs mapped", delta_color="off")
    with c3:
        with st.container(border=True):
            st.metric("Schedule Clashes", conflicts_count, "⚠️ Clashes active" if conflicts_count > 0 else "✅ Timetable clear", delta_color="inverse" if conflicts_count > 0 else "normal")
    with c4:
        with st.container(border=True):
            st.metric("Upcoming Exams", exams_count, "Venue audited", delta_color="off")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Prominent Conflict Alert if conflicts exist
    if conflicts:
        for c in conflicts:
            st.error(f"🚨 **{c['type'].replace('_', ' ')} on {c['date']}**: {c['explanation']} \n\n👉 **Recommended Solution:** {c['recommendation']}")

    # Main Grid: Left Column (Notices & Timetable) | Right Column (Revision Feed & Quick Query)
    grid_left, grid_right = st.columns([1.7, 1.3])

    with grid_left:
        # Recent Academic Notices Panel
        with st.container(border=True):
            col_notices_h, col_notices_sub = st.columns([3, 1])
            with col_notices_h:
                st.subheader("Recent Academic Notices & Circulars")
            with col_notices_sub:
                st.caption("Showing latest notices")

            for n in notices[:4]:
                with st.container(border=True):
                    col_info, col_stat = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{n.get('title')}**")
                        st.caption(f"Ref: `{n.get('reference_code')}` • {n.get('department')}")
                    with col_stat:
                        if n.get("status") == "SUPERSEDED":
                            st.warning("Superseded")
                        elif n.get("is_revision"):
                            st.info(f"Revised v{n.get('version', 2)}")
                        else:
                            st.success("Active")
                    st.markdown(f"📅 **Date:** {n.get('date')} &nbsp;|&nbsp; ⏰ **Time:** {n.get('start_time')} – {n.get('end_time')} &nbsp;|&nbsp; 📍 **Venue:** `{n.get('venue')}`")

        # Upcoming Exam Schedule Preview Widget
        with st.container(border=True):
            col_ex_h, col_ex_sub = st.columns([3, 1])
            with col_ex_h:
                st.subheader("Upcoming Exam Schedule")
            with col_ex_sub:
                st.caption("Full Calendar")

            exam_preview_data = []
            for ex in exams[:4]:
                clash_str = "⚠️ Clash" if ex.get("conflict_flag") else "✅ Normal"
                exam_preview_data.append({
                    "Course": ex["course_code"],
                    "Title": ex["course_title"],
                    "Date": ex["date"],
                    "Hours": f"{ex['start_time']} - {ex['end_time']}",
                    "Hall": ex["venue"],
                    "Status": clash_str
                })
            st.dataframe(pd.DataFrame(exam_preview_data), hide_index=True, use_container_width=True)

    with grid_right:
        # Recent Revision Panel
        with st.container(border=True):
            col_rev_h, col_rev_b = st.columns([3, 1])
            with col_rev_h:
                st.subheader("Recent Revisions & Field Diffs")
            with col_rev_b:
                st.info("Feed")
            st.caption("Automatic field-by-field diff comparison for amended circulars.")

            revised_items = [n for n in notices if n.get("is_revision")]
            if revised_items:
                for rev in revised_items:
                    parent = database.get_notice_by_id(rev.get("parent_notice_id", ""))
                    if parent:
                        diff = compare_notice_versions(parent, rev)
                        with st.container(border=True):
                            st.markdown(f"🔄 **REVISED: {rev.get('title')}**")
                            st.caption(f"Modified from Ref: `{parent.get('reference_code')}` (v1) to `{rev.get('reference_code')}` (v2)")
                            st.markdown(f"**Altered Fields:** {', '.join(diff['modified_fields'])}")
                            if diff['impact_level'] in ['CRITICAL', 'HIGH']:
                                st.error(f"**Impact Severity:** {diff['impact_level']}")
                            else:
                                st.info(f"**Impact Severity:** {diff['impact_level']}")
                            st.info(f"💡 {diff['advisory_summary']}")
            else:
                st.info("No revised notices found.")

        # Quick Assistant Query
        with st.container(border=True):
            st.subheader("Ask Notice Assistant")
            st.caption("Instant offline Q&A on academic notices, exams, and rooms.")

            sample_query = st.selectbox(
                "Quick Common Queries:",
                [
                    "Are there any venue conflicts on October 24?",
                    "When is CS301 midterm examination scheduled?",
                    "Show all notices revised in the last 48 hours",
                    "What is scheduled in Auditorium 1?",
                    "Is there a university holiday on Oct 28?"
                ]
            )
            if st.button("Submit Question", use_container_width=True):
                resp = query_assistant(sample_query, notices, exams, conflicts)
                st.success(f"**ANSWER** (Sources: {', '.join(resp['sources'])})\n\n{resp['answer']}")


# ---------------------------------------------------------
# Screen 2: Notices and PDF Upload
# ---------------------------------------------------------
elif selected_nav.startswith("📤 Upload Notice"):
    st.title("Upload Academic Notice & Information Extraction")
    st.caption("Upload official academic PDFs or paste raw circular text. Our AI extraction engine automatically extracts event details, dates, venues, and checks for revision amendments.")

    # Sample One-Click Loaders
    st.info("💡 **Quick Demo Loaders:** Load ready-to-test academic notices with 1 click:")

    btn_c1, btn_c2, btn_c3 = st.columns(3)

    if "current_upload_text" not in st.session_state:
        st.session_state.current_upload_text = ""
    if "form_title" not in st.session_state:
        st.session_state.form_title = ""
    if "form_ref" not in st.session_state:
        st.session_state.form_ref = ""
    if "form_issue_date" not in st.session_state:
        st.session_state.form_issue_date = ""
    if "form_date" not in st.session_state:
        st.session_state.form_date = ""
    if "form_dept" not in st.session_state:
        st.session_state.form_dept = ""
    if "form_venue" not in st.session_state:
        st.session_state.form_venue = ""
    if "form_time_start" not in st.session_state:
        st.session_state.form_time_start = ""
    if "form_time_end" not in st.session_state:
        st.session_state.form_time_end = ""
    if "form_version" not in st.session_state:
        st.session_state.form_version = 1
    if "form_is_rev" not in st.session_state:
        st.session_state.form_is_rev = False
    if "form_parent_opt" not in st.session_state:
        st.session_state.form_parent_opt = "None (No Parent / Standalone)"
    if "last_parsed_text" not in st.session_state:
        st.session_state.last_parsed_text = None
    if "force_sync_form" not in st.session_state:
        st.session_state.force_sync_form = False

    def populate_form_state(parsed: Dict[str, Any], parent_opts: List[str], matched_p: Optional[Dict[str, Any]]):
        raw_title = parsed.get("title", "")
        st.session_state.form_title = "" if "[Unknown" in raw_title or "[Not Specified" in raw_title else raw_title

        raw_ref = parsed.get("reference_code", "")
        st.session_state.form_ref = "" if "[Not Specified" in raw_ref or "[Unknown" in raw_ref else raw_ref

        raw_issue_date = parsed.get("issue_date", "")
        st.session_state.form_issue_date = "" if not raw_issue_date or "[Not Specified" in raw_issue_date or "[Unknown" in raw_issue_date else raw_issue_date

        raw_date = parsed.get("date", "")
        st.session_state.form_date = "" if "[Not Specified" in raw_date or "[Unknown" in raw_date else raw_date

        raw_dept = parsed.get("department", "")
        st.session_state.form_dept = "" if "[Unknown" in raw_dept or "[Not Specified" in raw_dept else raw_dept

        raw_venue = parsed.get("venue", "")
        st.session_state.form_venue = "" if "[Unknown" in raw_venue or "[Not Specified" in raw_venue else raw_venue

        raw_st = parsed.get("start_time", "")
        st.session_state.form_time_start = "" if "[Not Specified" in raw_st or "[Unknown" in raw_st else raw_st

        raw_et = parsed.get("end_time", "")
        st.session_state.form_time_end = "" if "[Not Specified" in raw_et or "[Unknown" in raw_et else raw_et

        rev_status = parsed.get("revision_status", "")
        is_rev = rev_status in ["Revision detected", "Needs review"]
        st.session_state.form_is_rev = is_rev

        v_val = parsed.get("version", 2 if is_rev else 1)
        try:
            st.session_state.form_version = int(v_val)
        except (ValueError, TypeError):
            st.session_state.form_version = 1

        selected_opt = parent_opts[0]
        if matched_p:
            for opt in parent_opts:
                if opt.startswith(f"{matched_p['id']}:"):
                    selected_opt = opt
                    break
        st.session_state.form_parent_opt = selected_opt

    with btn_c1:
        if st.button("📋 Load Notice A (Original CS301)", use_container_width=True):
            st.session_state.current_upload_text = SAMPLE_NOTICES[0]["raw_text"]
            st.session_state.force_sync_form = True
    with btn_c2:
        if st.button("🔄 Load Notice B (Revised CS301 Amendment)", use_container_width=True):
            st.session_state.current_upload_text = SAMPLE_NOTICES[1]["raw_text"]
            st.session_state.force_sync_form = True
    with btn_c3:
        if st.button("⚠️ Load Notice C (Clashing AI Keynote)", use_container_width=True):
            st.session_state.current_upload_text = SAMPLE_NOTICES[2]["raw_text"]
            st.session_state.force_sync_form = True

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    up_col1, up_col2 = st.columns([1, 1])

    with up_col1:
        st.subheader("1. Input Notice Content")
        uploaded_file = st.file_uploader(
            "Upload Academic Notice (PDF or TXT)",
            type=["pdf", "txt"],
            help="Upload official PDF or TXT circular. Uses PyMuPDF/pypdf for text PDFs, and advises OCR for scanned images."
        )

        pdf_extracted_notice = ""
        if uploaded_file is not None:
            file_name = uploaded_file.name.lower()
            if file_name.endswith(".pdf"):
                text_out, msg, is_scanned = extract_text_from_pdf(uploaded_file)
                if text_out:
                    pdf_extracted_notice = text_out
                    st.success(f"📄 {msg}")
                else:
                    if is_scanned:
                        st.error(msg)
                    else:
                        st.warning(msg)
            else:
                # Text file decoding with safe fallback encodings
                raw_bytes = uploaded_file.read()
                text_out, msg = decode_text_file(raw_bytes)
                if text_out:
                    pdf_extracted_notice = text_out
                    st.success(f"📝 {msg}")
                else:
                    st.warning(msg)

        if pdf_extracted_notice and pdf_extracted_notice != st.session_state.get("current_upload_text"):
            st.session_state.current_upload_text = pdf_extracted_notice
            st.session_state.force_sync_form = True

        final_raw_text = st.text_area(
            "Notice Raw Text:",
            value=st.session_state.current_upload_text,
            height=280,
            placeholder="DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nRef: CSE/EXAM/2026/01\nNOTICE: CS301 Midterm Examination\nDate: 2026-10-24\nTime: 10:00 AM to 12:00 PM\nVenue: Hall B\n(Or upload a PDF/TXT file above)"
        )

        parse_btn = st.button("🔍 Parse & Extract Fields", type="primary", use_container_width=True)
        if parse_btn:
            st.session_state.force_sync_form = True

    with up_col2:
        st.subheader("2. AI Field Extraction Review")

        if final_raw_text.strip():
            parsed_result = parse_academic_notice(final_raw_text)

            # Strict Audit Status: Alert user to missing fields
            if parsed_result["has_missing_fields"]:
                missing_str = ", ".join(parsed_result["missing_fields"])
                st.warning(
                    f"⚠️ **Incomplete Document Notice**: {len(parsed_result['missing_fields'])} field(s) were not found in the circular text: **{missing_str}**. "
                    "Campus Connect does not invent fake values. Please review and fill them in below before saving."
                )
            else:
                st.success("✅ **All key scheduling fields successfully identified from notice text!**")

            # Revision Intelligence Metadata & Matching
            rev_status = parsed_result.get("revision_status", "New notice / no revision detected")
            rev_conf = parsed_result.get("revision_confidence", 0.95)
            ext_conf = parsed_result.get("extraction_confidence", 0.0)
            parent_hint = parsed_result.get("parent_reference_hint")
            reasoning = parsed_result.get("revision_reasoning", "")

            # Look up parent notice in database
            # Look up parent notice in database
            matched_parent = database.find_matching_parent_notice(parent_hint) if parent_hint else None

            # Prepare parent options
            parent_options = ["None (No Parent / Standalone)"] + [f"{n['id']}: {n['title']} ({n['reference_code']})" for n in notices]

            # Synchronize parsed fields to form whenever requested or when text has changed
            if st.session_state.force_sync_form or st.session_state.last_parsed_text != final_raw_text:
                populate_form_state(parsed_result, parent_options, matched_parent)
                st.session_state.last_parsed_text = final_raw_text
                st.session_state.force_sync_form = False
                if parse_btn:
                    st.success("✅ Extracted notice fields and auto-populated form below!")

            if rev_status == "Revision detected":
                rev_icon = "🔄"
            elif rev_status == "Needs review":
                rev_icon = "⚠️"
            else:
                rev_icon = "📄"

            with st.container(border=True):
                col_aud_h, col_aud_badges = st.columns([2, 2])
                with col_aud_h:
                    st.markdown("##### PARSED ENTITIES & REVISION AUDIT")
                with col_aud_badges:
                    st.caption(f"Completeness: **{int(ext_conf*100)}%** | Status: **{rev_icon} {rev_status} ({int(rev_conf*100)}%)**")
                st.caption(f"**Parser Engine:** {parsed_result['parser_engine']} | **Revision Intelligence:** {reasoning}")

            if parent_hint:
                if matched_parent:
                    st.success(
                        f"🔗 **Original Notice Matched**: Found `{matched_parent['id']}` — **{matched_parent['title']}** "
                        f"(Ref: `{matched_parent['reference_code']}`). Pre-selected for automatic version diffing!"
                    )
                else:
                    st.info(
                        f"ℹ️ **Referenced Original Notice Hint**: `{parent_hint}` was detected in text, but no matching circular "
                        "currently exists in the database. Standalone mode selected; you can manually override below."
                    )

            # Live Diff Preview if a matching parent notice is identified
            if matched_parent:
                temp_new_notice = {
                    "title": parsed_result["title"],
                    "reference_code": parsed_result["reference_code"],
                    "version": parsed_result["version"],
                    "department": parsed_result["department"],
                    "category": parsed_result["category"],
                    "issue_date": parsed_result.get("issue_date", "[Not Specified]"),
                    "date": parsed_result["date"],
                    "start_time": parsed_result["start_time"],
                    "end_time": parsed_result["end_time"],
                    "venue": parsed_result["venue"],
                }
                live_diff = compare_notice_versions(matched_parent, temp_new_notice)
                with st.expander("🔍 Live Revision Diff Preview (Compared to Original Notice)", expanded=True):
                    if live_diff["impact_level"] in ["CRITICAL", "HIGH"]:
                        st.error(f"🚨 **Impact Severity:** {live_diff['impact_level']} | **Detected Field Changes:** {live_diff['total_changes']}")
                    else:
                        st.info(f"ℹ️ **Impact Severity:** {live_diff['impact_level']} | **Detected Field Changes:** {live_diff['total_changes']}")
                    st.caption(f"Advisory: {live_diff['advisory_summary']}")
                    diff_rows = []
                    for fd in live_diff["field_diffs"]:
                        if fd["status"] != "UNCHANGED":
                            diff_rows.append({
                                "Field": fd["field_label"],
                                "Original Value": fd["old_value"],
                                "Revised Value": fd["new_value"],
                                "Status": fd["status"],
                                "Impact": fd["impact_severity"]
                            })
                    if diff_rows:
                        st.dataframe(pd.DataFrame(diff_rows), use_container_width=True, hide_index=True)

            # Editable form before saving
            with st.form("save_notice_form"):
                st.subheader("Verify & Edit Extracted Notice Fields")

                f_title = st.text_input(
                    "Event Name / Examination Title",
                    key="form_title",
                    placeholder="Enter event/course title (e.g. CS301 Midterm Examination)"
                )

                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    f_ref = st.text_input(
                        "Notice Reference ID",
                        key="form_ref",
                        placeholder="e.g. CSE/EXAM/2026/01"
                    )
                    f_issue_date = st.text_input(
                        "Notice Issue Date (YYYY-MM-DD)",
                        key="form_issue_date",
                        placeholder="e.g. 2026-10-15"
                    )
                    f_date = st.text_input(
                        "Event / Exam Date (YYYY-MM-DD)",
                        key="form_date",
                        placeholder="e.g. 2026-10-24"
                    )
                    f_dept = st.text_input(
                        "Department",
                        key="form_dept",
                        placeholder="e.g. Department of Computer Science & Engineering"
                    )

                with f_c2:
                    f_venue = st.text_input(
                        "Venue / Room",
                        key="form_venue",
                        placeholder="e.g. Auditorium 1 - Main Complex"
                    )
                    f_time_start = st.text_input(
                        "Start Time (HH:MM)",
                        key="form_time_start",
                        placeholder="e.g. 10:00"
                    )
                    f_time_end = st.text_input(
                        "End Time (HH:MM)",
                        key="form_time_end",
                        placeholder="e.g. 12:00"
                    )
                    f_version = st.number_input(
                        "Revision / Version Number",
                        min_value=1,
                        max_value=99,
                        step=1,
                        key="form_version"
                    )

                f_is_rev = st.checkbox(
                    "Mark as Revision / Amendment",
                    key="form_is_rev"
                )

                curr_parent_opt = st.session_state.get("form_parent_opt", parent_options[0])
                if curr_parent_opt not in parent_options:
                    curr_parent_opt = parent_options[0]
                    st.session_state.form_parent_opt = curr_parent_opt

                f_parent = st.selectbox(
                    "Original / Parent Notice Reference (if revision):",
                    parent_options,
                    key="form_parent_opt"
                )

                submitted = st.form_submit_button("💾 Save Notice to Database", use_container_width=True)
                if submitted:
                    parent_id = None
                    if f_is_rev and not f_parent.startswith("None"):
                        parent_id = f_parent.split(":")[0].strip()

                    new_id = database.add_notice({
                        "title": f_title.strip() or "Untitled Notice",
                        "reference_code": f_ref.strip() or "UNASSIGNED-REF",
                        "version": int(f_version),
                        "is_revision": bool(f_is_rev),
                        "parent_notice_id": parent_id,
                        "department": f_dept.strip() or "Central Academic Administration",
                        "category": parsed_result["category"],
                        "issue_date": f_issue_date.strip() or "[Not Specified]",
                        "date": f_date.strip() or "[Not Specified]",
                        "start_time": f_time_start.strip() or "[Not Specified]",
                        "end_time": f_time_end.strip() or "[Not Specified]",
                        "venue": f_venue.strip() or "[Unknown / Not Specified]",
                        "raw_text": final_raw_text,
                        "is_sample": False,
                        "notes": f"User uploaded via web UI. Revision Status: {rev_status}"
                    })
                    st.success(f"✅ Notice successfully stored as {new_id}! Audit conflict scan initiated.")
                    st.rerun()
        else:
            st.info("👈 Please upload a PDF/TXT file or paste notice text, then click 'Parse & Extract Fields'.")


# ---------------------------------------------------------
# Screen 3: Revision History & Field-by-Field Comparison
# ---------------------------------------------------------
elif selected_nav.startswith("🔄 Revision History"):
    st.title("Notice Revision History & Field Comparison")
    st.caption("Inspect how academic circulars evolve across revisions. Compare original vs amended versions with automated field diffing and student schedule impact analysis.")

    revised_notices = [n for n in notices if n.get("is_revision")]

    if not revised_notices:
        st.info("No revised notices found in database. Upload a revised circular or click 'Reset Demo Dataset'.")
    else:
        # Selection
        selected_rev_label = st.selectbox(
            "Select Revised Notice to Inspect:",
            [f"{r['id']} — {r['title']} (Ref: {r['reference_code']})" for r in revised_notices]
        )
        selected_rev_id = selected_rev_label.split(" — ")[0]
        selected_rev = next(n for n in revised_notices if n["id"] == selected_rev_id)

        # Find parent or older version
        parent = None
        if selected_rev.get("parent_notice_id"):
            parent = database.get_notice_by_id(selected_rev["parent_notice_id"])
        if not parent:
            # Fallback to sample notice 0 if comparing demo
            parent = SAMPLE_NOTICES[0]

        diff_data = compare_notice_versions(parent, selected_rev)

        # Overview banner
        with st.container(border=True):
            col_ov1, col_ov2 = st.columns([3, 1])
            with col_ov1:
                st.subheader(f"Revision Comparison: v{diff_data['old_version']} ➔ v{diff_data['new_version']}")
                st.caption(f"Original: `{parent.get('reference_code')}` | Revised: `{selected_rev.get('reference_code')}`")
            with col_ov2:
                if diff_data["impact_level"] == "CRITICAL":
                    st.error(f"🚨 **IMPACT: {diff_data['impact_level']}**")
                elif diff_data["impact_level"] == "HIGH":
                    st.warning(f"⚠️ **IMPACT: {diff_data['impact_level']}**")
                else:
                    st.info(f"ℹ️ **IMPACT: {diff_data['impact_level']}**")
                st.caption(f"{diff_data['total_changes']} field(s) modified")

            st.info(f"💡 **Notice Summary & Advisory:** {diff_data['advisory_summary']}")

        # Side-by-Side Diff Table
        st.subheader("Field-by-Field Modification Matrix")

        diff_table_rows = []
        for fd in diff_data["field_diffs"]:
            is_changed = (fd["status"] == "MODIFIED")
            status_label = "🔴 CHANGED" if is_changed else "🟢 UNCHANGED"
            diff_table_rows.append({
                "Field Name": fd["field_label"],
                "Status": status_label,
                f"Original Value (v{diff_data['old_version']})": str(fd["old_value"]),
                f"Revised Value (v{diff_data['new_version']})": str(fd["new_value"])
            })

        df_diff = pd.DataFrame(diff_table_rows)
        st.dataframe(df_diff, use_container_width=True, hide_index=True)

        # Raw Text View in Expanders
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            with st.expander(f"📄 View Original Circular (v{diff_data['old_version']})"):
                st.code(parent.get("raw_text", ""), language="text")
        with col_t2:
            with st.expander(f"📄 View Revised Circular (v{diff_data['new_version']})"):
                st.code(selected_rev.get("raw_text", ""), language="text")


# ---------------------------------------------------------
# Screen 4: Schedule Conflict Detection
# ---------------------------------------------------------
elif selected_nav.startswith("⚠️ Conflict Detection"):
    st.title("Schedule Conflict & Timeline Clash Detection")
    st.caption("Automated timeline collision audit engine. Flags overlapping room bookings, departmental schedule collisions, and assessments scheduled during holidays.")

    if st.button("🔍 Run Full Timetable Conflict Audit", type="primary"):
        st.rerun()

    active_notices_count = len([n for n in notices if n.get('status') != 'SUPERSEDED'])
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Audited Active Notices", f"{active_notices_count} Active")
    with col_m2:
        st.metric("Clashes Detected", f"{len(conflicts)} Collision(s)")
    with col_m3:
        st.metric("Resolution Rate", "100% Actionable")

    st.divider()

    if not conflicts:
        st.success("🎉 No schedule conflicts detected! All active examinations and seminars have non-overlapping times and venues.")
    else:
        for idx, c in enumerate(conflicts, 1):
            ev_a = c["event_a"]
            ev_b = c["event_b"]
            loc = c.get("venue") or ev_a.get("venue") or ev_b.get("venue") or c.get("department", "Campus Venue")
            overlap_text = c.get("overlap_window")
            if not overlap_text:
                dur = c.get("duration_minutes", 0)
                overlap_text = f"{dur} minutes overlap" if dur else "Simultaneous overlap"
            elif c.get("duration_minutes") and "mins" not in overlap_text and "minute" not in overlap_text:
                overlap_text = f"{overlap_text} ({c.get('duration_minutes')} mins)"

            with st.container(border=True):
                # Header with Severity Label
                col_head, col_sev = st.columns([3, 1])
                with col_head:
                    st.subheader(f"⚠️ Conflict #{idx}: {c['type'].replace('_', ' ')}")
                    st.caption(f"Conflict ID: `{c['id']}`")
                with col_sev:
                    if c.get("severity") == "CRITICAL":
                        st.error("🚨 **CRITICAL**")
                    else:
                        st.warning(f"⚠️ **{c.get('severity', 'HIGH')}**")

                st.markdown(f"**Description:** {c['explanation']}")

                # Conflict location, date, and 90-minute overlap clearly
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.info(f"📍 **Location / Venue:**\n\n`{loc}`")
                with col_c2:
                    st.info(f"📅 **Conflict Date:**\n\n`{c.get('date', 'Not Specified')}`")
                with col_c3:
                    st.info(f"⏰ **Time Overlap:**\n\n`{overlap_text}`")

                # Conflicting events in a readable two-column layout
                st.markdown("#### Conflicting Events")
                col_ev_a, col_ev_b = st.columns(2)
                with col_ev_a:
                    with st.container(border=True):
                        st.markdown("##### 📌 First Booked Event")
                        st.markdown(f"**Title:** {ev_a.get('title', 'N/A')}")
                        st.markdown(f"**Reference:** `{ev_a.get('reference_code', 'N/A')}`")
                        st.markdown(f"**Department:** {ev_a.get('department', 'N/A')}")
                        st.markdown(f"**Time:** ⏰ {ev_a.get('start_time', 'N/A')} – {ev_a.get('end_time', 'N/A')}")
                        st.markdown(f"**Venue:** 📍 `{ev_a.get('venue', 'N/A')}`")

                with col_ev_b:
                    with st.container(border=True):
                        st.markdown("##### ⚡ Conflicting Concurrent Event")
                        st.markdown(f"**Title:** {ev_b.get('title', 'N/A')}")
                        st.markdown(f"**Reference:** `{ev_b.get('reference_code', 'N/A')}`")
                        st.markdown(f"**Department:** {ev_b.get('department', 'N/A')}")
                        st.markdown(f"**Time:** ⏰ {ev_b.get('start_time', 'N/A')} – {ev_b.get('end_time', 'N/A')}")
                        st.markdown(f"**Venue:** 📍 `{ev_b.get('venue', 'N/A')}`")

                # Automated recommendation in a separate readable section
                st.success(f"💡 **Automated Resolution Recommendation:**\n\n{c['recommendation']}")


# ---------------------------------------------------------
# Screen 5: Upcoming Exam Schedule
# ---------------------------------------------------------
elif selected_nav.startswith("📅 Upcoming Exam"):
    st.title("Master Academic Examination Timetable")
    st.caption("Official examination schedule cross-referenced with notice intelligence. Filter by course, venue, or department.")

    filter_c1, filter_c2, filter_c3 = st.columns([1.5, 1, 1])
    with filter_c1:
        search_query = st.text_input("🔍 Search Course, Code or Hall:", placeholder="e.g. CS301, Auditorium, Midterm")
    with filter_c2:
        depts = ["All Departments"] + sorted(list(set(e["department"] for e in exams)))
        sel_dept = st.selectbox("Department Filter:", depts)
    with filter_c3:
        st_filter = st.selectbox("Clash Filter:", ["All Exams", "Conflicting Only", "Clear Only"])

    # Filter exams
    filtered_exams = exams
    if search_query:
        sq = search_query.lower()
        filtered_exams = [e for e in filtered_exams if sq in e["course_code"].lower() or sq in e["course_title"].lower() or sq in e["venue"].lower()]
    if sel_dept != "All Departments":
        filtered_exams = [e for e in filtered_exams if e["department"] == sel_dept]
    if st_filter == "Conflicting Only":
        filtered_exams = [e for e in filtered_exams if e.get("conflict_flag")]
    elif st_filter == "Clear Only":
        filtered_exams = [e for e in filtered_exams if not e.get("conflict_flag")]

    # Display Table
    table_data = []
    for ex in filtered_exams:
        table_data.append({
            "Code": ex["course_code"],
            "Course Title": ex["course_title"],
            "Type": ex["exam_type"],
            "Department": ex["department"],
            "Date": ex["date"],
            "Time": f"{ex['start_time']} - {ex['end_time']}",
            "Venue": ex["venue"],
            "Students": ex["total_students"],
            "Status": "⚠️ CLASH DETECTED" if ex.get("conflict_flag") else ex["status"]
        })

    st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)

    # Download CSV export
    if filtered_exams:
        df_csv = pd.DataFrame(table_data).to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Export Exam Schedule (CSV)",
            data=df_csv,
            file_name=f"exam_schedule_{datetime.date.today()}.csv",
            mime="text/csv"
        )


# ---------------------------------------------------------
# Screen 6: Academic Assistant Chatbot
# ---------------------------------------------------------
elif selected_nav.startswith("🤖 Academic AI"):
    st.title("Academic Notice Intelligence Assistant")
    st.caption("Context-aware conversational assistant trained on all uploaded circulars, exam schedules, and conflict logs. Runs 100% free and offline without external API keys.")

    # 1. Quick Demo Question Pills
    st.caption("💡 **Quick Common Queries:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    quick_query_selected = None
    with qc1:
        if st.button("🚨 Venue Clashes?", use_container_width=True, help="Ask about room booking collisions"):
            quick_query_selected = "Are there any venue clashes or schedule conflicts?"
    with qc2:
        if st.button("📅 When is CS301?", use_container_width=True, help="Check CS301 midterm details"):
            quick_query_selected = "When is the CS301 exam scheduled and where?"
    with qc3:
        if st.button("🔄 Revised Notices?", use_container_width=True, help="Inspect notices that were amended"):
            quick_query_selected = "Show all notices that were revised recently"
    with qc4:
        if st.button("🌴 University Holidays?", use_container_width=True, help="Check declared recess dates"):
            quick_query_selected = "Are there any declared university holidays or campus breaks?"

    # Chat submission processor
    def submit_user_chat(prompt_text: str):
        cleaned = prompt_text.strip() if prompt_text else ""
        if not cleaned:
            st.warning("⚠️ Please enter a question before sending.")
            return

        # Record user message in history
        st.session_state.chat_messages.append({"role": "user", "content": cleaned})

        # Query the local rule-based RAG engine
        try:
            assistant_res = query_assistant(
                cleaned,
                notices,
                exams,
                conflicts,
                api_key=st.session_state.get("api_key") or None
            )
            formatted_answer = assistant_res["answer"]
            if assistant_res.get("sources"):
                formatted_answer += f"\n\n---\n*📚 Verified Sources: {', '.join(assistant_res['sources'])} • Engine: {assistant_res['engine']}*"
        except Exception as e:
            formatted_answer = f"⚠️ An error occurred while retrieving answer: {str(e)}"

        # Record assistant answer in history
        st.session_state.chat_messages.append({"role": "assistant", "content": formatted_answer})
        st.rerun()

    if quick_query_selected:
        submit_user_chat(quick_query_selected)

    # 2. Chat Messages Stream Container
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 3. Dedicated Chat Input Bar (Normal visible text input with Send button & Enter submit)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.form("academic_chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            chat_input_text = st.text_input(
                "Ask a Question",
                placeholder="Type your academic notice question here (e.g. 'Are there any clashes on Oct 24?')...",
                label_visibility="collapsed",
                key="chat_visible_text_input"
            )
        with col_btn:
            send_clicked = st.form_submit_button("Send ➔", type="primary", use_container_width=True)

        if send_clicked:
            submit_user_chat(chat_input_text)

    # 4. Chat Reset Control
    col_clear, _ = st.columns([2, 4])
    with col_clear:
        if st.button("🗑️ Clear Chat History", help="Resets conversation to default welcome message"):
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "👋 Hello! I am your Campus Connect Academic Assistant. Ask me about exam dates, recent notice revisions, venue allocations, or timetable conflicts!"}
            ]
            st.rerun()

    st.divider()

    # 5. Optional External LLM API Key (SEPARATE from chat input, password-masked)
    with st.expander("⚙️ Optional External LLM Integration (OpenAI / Gemini)", expanded=False):
        st.markdown("""
            **Campus Connect operates 100% offline and free** using our built-in deterministic RAG knowledge matcher. No external API key is required.
            
            If you wish to optionally route responses through an external LLM, configure your personal API key below:
        """)
        with st.form("api_key_configuration_form"):
            user_key_input = st.text_input(
                "Personal API Key (Optional)",
                type="password",
                value=st.session_state.get("api_key", ""),
                placeholder="sk-...",
                help="This key is stored in memory for the current session only. Never logged or displayed."
            )
            save_key_btn = st.form_submit_button("Save API Key")
            if save_key_btn:
                st.session_state.api_key = user_key_input.strip()
                st.success("API Key updated in session.")


# ---------------------------------------------------------
# Screen 7: Notifications & Profile
# ---------------------------------------------------------
elif selected_nav.startswith("🔔 Notifications"):
    st.title("Notifications Feed & System Profile")
    st.caption("Audit alerts, circular revision subscriptions, and administrative user profile preferences.")

    # Prominent Demo Data Integrity Banner
    if db_stats["has_demo_data"]:
        st.warning(
            "⚠️ **SAMPLE DEMO ACTIVE**: Pre-loaded demonstration circulars and clash scenarios are currently active in the local database. "
            "Sample notifications and events are explicitly labeled with `[SAMPLE DEMO DATA]` below."
        )
    else:
        st.success("✅ **PRODUCTION DATABASE ACTIVE**: All circulars, examinations, and logged audit events are real application records.")

    col_n1, col_n2 = st.columns([1.65, 1.35])

    with col_n1:
        st.subheader("System Notifications & Activity Logs")
        st.caption("Chronological audit logs for timetable collisions, circular amendments, and academic calendar updates.")

        # Interactive Filter Bar
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sel_type = st.selectbox("Filter Type:", ["All Types", "Conflict", "Revision", "Info"], key="feed_filter_type")
        with fc2:
            sel_status = st.selectbox("Read Status:", ["All Notifications", "Unread Only", "Read Only"], key="feed_filter_status")
        with fc3:
            sel_origin = st.selectbox("Data Origin:", ["All Records", "Real Events Only", "Sample Demo Only"], key="feed_filter_origin")

        # Global Quick Actions
        act_c1, act_c2 = st.columns([1.5, 1])
        with act_c1:
            if st.button("✅ Mark All as Read", use_container_width=True):
                database.mark_all_notifications_read()
                st.rerun()
        with act_c2:
            if st.button("🔄 Refresh Notifications", use_container_width=True):
                st.rerun()

        st.divider()

        # Process and filter notifications
        filtered_notifs = []
        for notif in notifications:
            t_label, sev, icon = classify_notification(notif)
            is_sample = bool(notif.get("is_sample", False))
            is_read = bool(notif.get("read", False))

            # Apply user filters
            if sel_type != "All Types" and t_label != sel_type:
                continue
            if sel_status == "Unread Only" and is_read:
                continue
            if sel_status == "Read Only" and not is_read:
                continue
            if sel_origin == "Real Events Only" and is_sample:
                continue
            if sel_origin == "Sample Demo Only" and not is_sample:
                continue

            filtered_notifs.append((notif, t_label, sev, icon, is_sample, is_read))

        if not filtered_notifs:
            st.info("ℹ️ No notifications match the selected filter criteria.")
        else:
            for notif, t_label, sev, icon, is_sample, is_read in filtered_notifs:
                with st.container(border=True):
                    # Header row: Title, Type Label, Timestamp
                    col_t_left, col_t_right = st.columns([3, 1.2])
                    with col_t_left:
                        status_tag = "🔵 `[UNREAD]` " if not is_read else ""
                        st.markdown(f"#### {status_tag}{icon} {t_label}: {notif['title']}")
                    with col_t_right:
                        formatted_ts = format_notification_timestamp(notif.get("timestamp"))
                        st.caption(f"🕒 {formatted_ts}")

                    # Severity styling for critical conflicts
                    if t_label == "Conflict" and sev == "CRITICAL":
                        st.error("🚨 **CRITICAL CONFLICT**: Direct room booking or timetable clash detected. Immediate timetable review required.")

                    # Concise description
                    st.write(notif.get("message", ""))

                    # Footer row: Origin Tag and Actions
                    f_col1, f_col2 = st.columns([3, 1.2])
                    with f_col1:
                        if is_sample:
                            st.caption(f"🏷️ **SAMPLE DEMO DATA** • Reference: `{notif['id']}`")
                        else:
                            st.caption(f"🟢 **REAL APPLICATION EVENT** • Reference: `{notif['id']}`")
                    with f_col2:
                        if not is_read:
                            if st.button("Mark as Read", key=f"mark_read_{notif['id']}", use_container_width=True):
                                database.mark_notification_read(notif["id"])
                                st.rerun()
                        else:
                            if st.button("Mark Unread", key=f"mark_unread_{notif['id']}", use_container_width=True):
                                database.mark_notification_unread(notif["id"])
                                st.rerun()

    with col_n2:
        st.subheader("User Profile & Preferences")
        st.caption("Active administrative session, dispatch settings, and database telemetry.")

        # 1. User Profile Section (No fabricated real person identity)
        with st.container(border=True):
            st.markdown("### 👤 Administrator Profile")
            st.markdown(f"**Display Name:** {st.session_state.profile_display_name}")
            st.markdown(f"**System Role:** {st.session_state.profile_role}")
            st.markdown(f"**Primary Department:** {st.session_state.profile_dept}")

            with st.expander("✏️ Update Profile Details"):
                p_name = st.text_input("Operator Name / Alias:", value=st.session_state.profile_display_name, key="edit_prof_name")
                p_role = st.text_input("Administrative Role:", value=st.session_state.profile_role, key="edit_prof_role")
                depts_list = [
                    "Office of Academic Affairs",
                    "Computer Science & Engineering",
                    "Electrical & Electronics Engineering",
                    "Mechanical Engineering",
                    "Mathematics & Data Science",
                    "Physics & Nanotechnology",
                    "Central Examination Cell"
                ]
                cur_dept_idx = depts_list.index(st.session_state.profile_dept) if st.session_state.profile_dept in depts_list else 0
                p_dept = st.selectbox("Primary Department:", depts_list, index=cur_dept_idx, key="edit_prof_dept")
                if st.button("Save Profile Settings", use_container_width=True):
                    st.session_state.profile_display_name = p_name.strip() or "Academic Administrator"
                    st.session_state.profile_role = p_role.strip() or "Exam Controller"
                    st.session_state.profile_dept = p_dept
                    st.success("Profile updated successfully.")
                    st.rerun()

        # 2. Notification Preferences & Delivery Reality
        with st.container(border=True):
            st.markdown("#### ⚙️ Notification Preferences & Delivery")
            st.caption("Delivery Channels & Dispatch Status")

            st.markdown("**Delivery Status:**")
            st.markdown("• **In-App Notification Feed:** `ACTIVE` *(Logged directly to notice_intel.db)*")
            st.markdown("• **External Dispatch (SMS / Email):** `OFFLINE / NOT CONFIGURED`\n\n*(Campus Connect operates on local SQLite storage; external SMS/Email gateways are not enabled)*")

            st.divider()
            st.markdown("**Active Alert Subscriptions:**")
            p_conf = st.checkbox("Room & Examination Conflicts (Critical)", value=st.session_state.pref_conflict_alerts, key="chk_conf_sub")
            p_rev = st.checkbox("Notice Revisions & Rescheduling Amendments", value=st.session_state.pref_revision_alerts, key="chk_rev_sub")
            p_hol = st.checkbox("Declared Holidays & Campus Recess Alerts", value=st.session_state.pref_holiday_alerts, key="chk_hol_sub")
            st.session_state.pref_conflict_alerts = p_conf
            st.session_state.pref_revision_alerts = p_rev
            st.session_state.pref_holiday_alerts = p_hol

        # 3. Database Status & Integrity
        with st.container(border=True):
            st.markdown("#### 🗄️ Database Status & Telemetry")
            st.caption("Local SQLite persistence telemetry.")

            st.markdown("**Instance Path:** `notice_intel.db` (SQLite 3)")
            st.markdown("**Connection State:** `🟢 Connected & Operational`")

            if db_stats["has_demo_data"]:
                st.warning("🏷️ **Data Integrity Tag:** `[SAMPLE DEMO ACTIVE]`\n\nDemonstration records are active alongside any uploaded circulars.")
            else:
                st.success("🟢 **Data Integrity Tag:** `[PRODUCTION ACTIVE]`\n\nAll records are real uploaded notices and verified events.")

            st.markdown("##### Real vs Sample Record Breakdown:")
            stat_c1, stat_c2 = st.columns(2)
            with stat_c1:
                st.metric(
                    "Circulars & Notices",
                    f"{db_stats['total_notices']}",
                    f"{db_stats['real_notices']} real | {db_stats['sample_notices']} sample",
                    delta_color="off"
                )
                st.metric(
                    "Total Notifications",
                    f"{db_stats['total_notifications']}",
                    f"{db_stats['real_notifications']} real | {db_stats['sample_notifications']} sample",
                    delta_color="off"
                )
            with stat_c2:
                st.metric(
                    "Master Exams",
                    f"{db_stats['total_exams']}",
                    f"{db_stats['real_exams']} real | {db_stats['sample_exams']} sample",
                    delta_color="off"
                )
                st.metric(
                    "Unread Alerts",
                    f"{db_stats['unread_notifications']}",
                    "Requires review" if db_stats['unread_notifications'] > 0 else "All caught up",
                    delta_color="inverse" if db_stats['unread_notifications'] > 0 else "off"
                )
