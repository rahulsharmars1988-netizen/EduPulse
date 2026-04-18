"""
EduPulse — Streamlit entrypoint (Home).

Run:
    streamlit run app.py
"""
import pandas as pd
import streamlit as st

from config import APP_NAME, APP_TAGLINE
from ui import (
    hero,
    inject_css,
    footer,
    section_title,
    divider,
    callout,
    render_decision_dashboard,
)
import storage


st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

storage.all_workspaces()

hero(
    f"{APP_NAME} — {APP_TAGLINE}",
    "Multi-layer institutional diagnostics for continuity, programme vitality, and market alignment.",
)


# ---------------------------------------------------------------------------
# Product intro
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])
with col1:
    st.subheader("What EduPulse is")
    st.write(
        "EduPulse is a **multi-layer institutional health diagnostics engine**. "
        "It evaluates your institution across three deterministic frameworks:"
    )
    st.markdown(
        "- **ICG — Institutional Continuity / Faculty System**  \n"
        "  Continuity, dependency, succession, and attrition exposure.\n"
        "- **DMM — Programme Vitality / Outcome System**  \n"
        "  Alignment, adaptation, value, degree–job fit, contribution, teaching effectiveness.\n"
        "- **GPIS — Geo-Pedagogical / Market Alignment System**  \n"
        "  Supply–demand fit across domain × geography."
    )
    st.caption(
        "EduPulse is **not** a ranking system, a compliance dashboard, or a data warehouse. "
        "It is a self-assessment and improvement layer."
    )

with col2:
    st.subheader("How it works")
    st.markdown(
        "1. **Download** the official EduPulse template.\n"
        "2. **Fill** the four input sheets using the dropdowns.\n"
        "3. **Upload** the same workbook back.\n"
        "4. **Run** Internal, External, or Both reports from the same upload.\n"
        "5. **Download** the generated PDF(s) with your branding.\n"
        "6. **Compare** up to 3 cases side-by-side."
    )
    st.info("All processing happens in your active session. No data is stored server-side.")

divider()


# ---------------------------------------------------------------------------
# Quick actions
# ---------------------------------------------------------------------------
section_title("Quick actions")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("📥 Download Template", use_container_width=True, key="qa_download_template"):
        st.switch_page("pages/1_Download_Template.py")
with c2:
    if st.button("⬆️ Upload Case", use_container_width=True, key="qa_upload_case"):
        st.switch_page("pages/2_Upload_Case.py")
with c3:
    if st.button("📊 Analysis & Reports", use_container_width=True, key="qa_analysis"):
        st.switch_page("pages/3_Analysis.py")
with c4:
    if st.button("🔁 Compare Cases", use_container_width=True, key="qa_compare"):
        st.switch_page("pages/4_Compare_Cases.py")
with c5:
    if st.button("⚙️ Report Settings", use_container_width=True, key="qa_settings"):
        st.switch_page("pages/6_Report_Settings.py")


# ---------------------------------------------------------------------------
# Active case — decision dashboard
# ---------------------------------------------------------------------------
ws_all = storage.all_workspaces()

active = None
active_name = st.session_state.get("active_workspace_name")
if active_name:
    active = storage.get_workspace(active_name)
if active is None and ws_all:
    active = ws_all[-1]
    st.session_state["active_workspace_name"] = active.name

if active is not None:
    divider()
    section_title(f"Decision Dashboard — {active.name}")
    st.caption(
        f"Source file: {active.original_filename or '—'} · "
        f"Uploaded {active.uploaded_at} · Workspace ID: {active.workspace_id}"
    )

    if len(ws_all) > 1:
        names = [w.name for w in ws_all]
        default_idx = names.index(active.name) if active.name in names else 0
        picked = st.selectbox("Active case", names, index=default_idx, key="home_active_case_picker")
        if picked and picked != active.name:
            st.session_state["active_workspace_name"] = picked
            st.rerun()

    try:
        integrated = active.integrated or {}
        confidence = active.confidence or {}

        dashboard_payload = {
            "state": integrated.get("state"),
            "score": integrated.get("score"),
            "confidence": confidence.get("label") or confidence.get("composite_score"),
            "framework_scores": {
                "ICG": (active.icg or {}).get("score"),
                "DMM": (active.dmm or {}).get("score"),
                "GPIS": (active.gpis or {}).get("score"),
            },
            "decision_summary": integrated.get("override_reason"),
        }

        render_decision_dashboard(dashboard_payload)
    except Exception as e:
        st.warning(f"Dashboard could not be rendered: {e}")

    divider()
    section_title("Go deeper")
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("🔎 Open full Analysis", use_container_width=True, key="gd_analysis"):
            st.switch_page("pages/3_Analysis.py")
    with d2:
        if st.button("🔁 Compare with other cases", use_container_width=True, key="gd_compare"):
            st.switch_page("pages/4_Compare_Cases.py")
    with d3:
        if st.button("⬆️ Upload another case", use_container_width=True, key="gd_upload"):
            st.switch_page("pages/2_Upload_Case.py")

    if not active.has_internal() or not active.has_external():
        callout(
            "Generate reports for this case from the Analysis page, or run them quickly below."
        )
        rb1, rb2, rb3 = st.columns(3)
        with rb1:
            if st.button(
                "▶ Run Internal",
                use_container_width=True,
                disabled=active.has_internal(),
                key="home_run_internal",
            ):
                active.run_internal()
                st.rerun()
        with rb2:
            if st.button(
                "▶ Run External",
                use_container_width=True,
                disabled=active.has_external(),
                key="home_run_external",
            ):
                active.run_external()
                st.rerun()
        with rb3:
            if st.button("▶ Generate Both", use_container_width=True, key="home_run_both"):
                active.run_both()
                st.rerun()

else:
    divider()
    callout(
        "No case loaded yet. Use **Upload Case** to load a filled EduPulse workbook — "
        "the decision dashboard will appear here automatically."
    )


# ---------------------------------------------------------------------------
# Cases in session
# ---------------------------------------------------------------------------
if ws_all:
    divider()
    section_title("Cases in this session")
    df = pd.DataFrame([w.summary_row() for w in ws_all])
    st.dataframe(df, use_container_width=True, hide_index=True)


footer()
