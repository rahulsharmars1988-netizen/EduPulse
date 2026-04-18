"""Upload a filled EduPulse workbook, validate + score, save as a workspace."""
import streamlit as st

from case import build_workspace, derive_case_name
import storage
from ui import (
    hero, inject_css, footer, section_title, divider, callout,
    render_decision_dashboard,
)

st.set_page_config(page_title="EduPulse — Upload Case", page_icon="⬆️", layout="wide")
inject_css()
hero("Upload a filled EduPulse workbook")

up = st.file_uploader(
    "EduPulse workbook (.xlsx)",
    type=["xlsx"],
    help="Upload the same file you downloaded from the template page, with your data filled in.",
    key="uploader",
)

if up is None:
    st.info("Upload a workbook to begin. The case name is auto-derived from the filename and editable below.")
    footer()
    st.stop()

derived = derive_case_name(up.name)

c1, c2 = st.columns([2, 1])
with c1:
    case_name = st.text_input(
        "Case name (editable)",
        value=st.session_state.get("pending_case_name", derived),
        help="Auto-filled from the uploaded filename. Change it before you run analysis if you want.",
        key="case_name_input",
    )
with c2:
    st.caption(f"Source file: **{up.name}**")
    st.caption(f"Auto-name: **{derived}**")

st.session_state["pending_case_name"] = case_name

run = st.button("Validate & score workbook", type="primary", use_container_width=True)

if run:
    if not case_name.strip():
        st.error("Please give the case a name before running.")
        st.stop()
    existing = storage.get_workspace(case_name.strip())
    if existing:
        st.warning(
            f"A case named **{existing.name}** already exists in this session. "
            "Continuing will replace it."
        )

    with st.spinner("Validating and scoring…"):
        xls_bytes = up.read()
        ws = build_workspace(xls_bytes, case_name=case_name.strip(), original_filename=up.name)

    if not ws.validation.ok:
        st.error("Validation failed — the workbook does not match the EduPulse template.")
        for e in ws.validation.errors:
            st.write(f"• {e}")
        st.stop()

    storage.add_workspace(ws)
    st.session_state["active_workspace_name"] = ws.name

    if ws.validation.warnings:
        with st.expander(f"⚠️ {len(ws.validation.warnings)} validation warning(s) (non-blocking)", expanded=False):
            for w in ws.validation.warnings:
                st.write(f"• {w}")

    st.success(f"Case **{ws.name}** saved.")

active_name = st.session_state.get("active_workspace_name")
if not active_name:
    footer()
    st.stop()

ws = storage.get_workspace(active_name)
if not ws:
    footer()
    st.stop()

divider()
section_title(f"Case: {ws.name}")
st.caption(
    f"Source file: {ws.original_filename} · Uploaded {ws.uploaded_at} · Workspace ID: {ws.workspace_id}"
)

try:
    render_decision_dashboard(ws)
except Exception as e:
    st.warning(f"Dashboard could not be rendered: {e}")

divider()
section_title("Generate reports")
st.write("Run one mode, the other, or both. Results stay in this session — no re-upload needed.")

b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("▶ Run Internal Analysis", use_container_width=True,
                 type="primary" if not ws.has_internal() else "secondary",
                 key="upl_run_internal"):
        ws.run_internal()
        st.success("Internal report generated.")
        st.rerun()
with b2:
    if st.button("▶ Run External Analysis", use_container_width=True,
                 type="primary" if not ws.has_external() else "secondary",
                 key="upl_run_external"):
        ws.run_external()
        st.success("External report generated.")
        st.rerun()
with b3:
    if st.button("▶ Generate Both Reports", use_container_width=True, key="upl_run_both"):
        ws.run_both()
        st.success("Both reports generated.")
        st.rerun()
with b4:
    if st.button("✕ Clear Case", use_container_width=True, key="upl_clear"):
        storage.remove_workspace(ws.name)
        st.session_state.pop("active_workspace_name", None)
        st.rerun()

if ws.has_internal() or ws.has_external():
    callout(
        "Open the **Analysis** page to drill into framework detail, download PDFs, "
        "and compare internal vs external renderings of this same case."
    )
    if st.button("→ Go to Analysis", use_container_width=True, key="upl_to_analysis"):
        st.switch_page("pages/3_Analysis.py")

footer()
