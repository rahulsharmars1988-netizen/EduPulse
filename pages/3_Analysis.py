"""Analysis — decision dashboard, framework detail, and PDF downloads."""
import pandas as pd
import streamlit as st

import storage
from report import render_internal_pdf, render_external_pdf

try:
    from branding import load_settings
    _HAS_BRANDING = True
except Exception:
    _HAS_BRANDING = False

try:
    from report_compose import diff_modes
    _HAS_DIFF = True
except Exception:
    _HAS_DIFF = False

from ui import (
    hero, inject_css, footer, section_title, divider, callout,
    render_decision_dashboard,
)

st.set_page_config(page_title="EduPulse — Analysis", page_icon="📊", layout="wide")
inject_css()
hero("Analysis & reports")

workspaces = storage.all_workspaces()
if not workspaces:
    st.info("No cases yet. Upload a workbook first.")
    if st.button("→ Go to Upload Case", use_container_width=True, key="ana_go_upload"):
        st.switch_page("pages/2_Upload_Case.py")
    footer()
    st.stop()

names = [w.name for w in workspaces]
default = st.session_state.get("active_workspace_name")
default_idx = names.index(default) if default in names else 0
selected = st.sidebar.radio("Cases in session", names, index=default_idx, key="ana_sidebar_case")
st.session_state["active_workspace_name"] = selected
if st.sidebar.button("🗑 Remove this case", use_container_width=True, key="ana_remove_case"):
    storage.remove_workspace(selected)
    st.session_state.pop("active_workspace_name", None)
    st.rerun()

ws = storage.get_workspace(selected)
if not ws:
    footer()
    st.stop()

branding = load_settings() if _HAS_BRANDING else None

section_title(f"Case: {ws.name}")
st.caption(
    f"Source file: {ws.original_filename or '—'} · Uploaded {ws.uploaded_at} · Workspace ID: {ws.workspace_id}"
)

try:
    render_decision_dashboard(ws)
except Exception as e:
    st.warning(f"Dashboard could not be rendered: {e}")

divider()
r1, r2, r3 = st.columns(3)
with r1:
    if st.button(("↻ Re-run Internal" if ws.has_internal() else "▶ Run Internal"),
                 use_container_width=True, key="ana_run_internal"):
        ws.run_internal()
        st.rerun()
with r2:
    if st.button(("↻ Re-run External" if ws.has_external() else "▶ Run External"),
                 use_container_width=True, key="ana_run_external"):
        ws.run_external()
        st.rerun()
with r3:
    if st.button("▶ Generate Both", use_container_width=True, key="ana_run_both"):
        ws.run_both()
        st.rerun()

divider()

tab_ana, tab_int, tab_ext, tab_cmp = st.tabs(
    ["🔎 Analysis detail", "🔒 Internal Report", "🌐 External Report", "⇌ Compare Modes"]
)

# ---------------- Analysis detail ----------------
with tab_ana:
    section_title("Confidence breakdown")
    conf = ws.confidence or {}
    if conf.get("dimensions"):
        rows = [
            {"Dimension": k.replace("_", " ").title(), "Score": f"{v['score']:.1f}", "Note": v["note"]}
            for k, v in conf["dimensions"].items()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"Composite: **{conf.get('composite_score', '—')}** · Label: **{conf.get('label', '—')}**")
    else:
        st.caption("Confidence detail unavailable.")

    # ICG
    section_title("ICG — Institutional Continuity / Faculty System")
    icg = ws.icg or {}
    if icg.get("available"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("State", icg["state"])
        m2.metric("Score", f"{icg['score']:.1f}")
        m3.metric("High-risk faculty", f"{icg['high_risk_count']} / {icg['faculty_count']}")
        m4.metric("Coverage", f"{icg['coverage_pct']:.0f}%")
        if icg.get("key_drivers"):
            with st.expander("Key drivers", expanded=True):
                for d in icg["key_drivers"]:
                    st.markdown(f"- {d}")
        if icg.get("dept_concentration") is not None:
            st.markdown("**Department concentration**")
            st.dataframe(icg["dept_concentration"], use_container_width=True, hide_index=True)
        if icg.get("flagged_faculty") is not None:
            st.markdown("**Top flagged faculty**")
            st.dataframe(icg["flagged_faculty"], use_container_width=True, hide_index=True)
    else:
        st.info(icg.get("reason", "ICG unavailable."))

    # DMM
    divider()
    section_title("DMM — Programme Vitality / Outcome System")
    dmm = ws.dmm or {}
    if dmm.get("available"):
        m1, m2, m3 = st.columns(3)
        m1.metric("State", dmm["state"])
        m2.metric("Mean score", f"{dmm['score']:.1f}")
        m3.metric("Coverage", f"{dmm['coverage_pct']:.0f}%")
        if dmm.get("key_drivers"):
            with st.expander("Key drivers", expanded=True):
                for d in dmm["key_drivers"]:
                    st.markdown(f"- {d}")
        if dmm.get("sub_means"):
            st.markdown("**Sub-score means across programmes**")
            st.dataframe(
                pd.DataFrame(list(dmm["sub_means"].items()), columns=["Sub-score", "Mean"]),
                use_container_width=True, hide_index=True,
            )
        if dmm.get("programme_table") is not None:
            st.markdown("**Programme vitality table**")
            st.dataframe(dmm["programme_table"], use_container_width=True, hide_index=True)
        if dmm.get("anti_gaming_flags"):
            with st.expander(f"⚠️ Anti-gaming flags ({len(dmm['anti_gaming_flags'])})", expanded=False):
                flag_rows = [
                    {
                        "Category": f.get("category", "—"),
                        "Severity": f.get("severity", "—"),
                        "Affected": f.get("affected_unit", "—"),
                        "Reason": f.get("reason", "—"),
                        "Suggested action": f.get("suggested_action", "—"),
                    }
                    for f in dmm["anti_gaming_flags"]
                ]
                st.dataframe(pd.DataFrame(flag_rows), use_container_width=True, hide_index=True)
                st.caption("Anti-gaming flags appear on this page and in Internal reports only.")
    else:
        st.info(dmm.get("reason", "DMM unavailable."))

    # GPIS
    divider()
    section_title("GPIS — Geo-Pedagogical / Market Alignment System")
    gpis = ws.gpis or {}
    if gpis.get("available"):
        m1, m2, m3 = st.columns(3)
        m1.metric("State", gpis["state"])
        m2.metric("Score", f"{gpis['score']:.1f}")
        m3.metric("Coverage", f"{gpis['coverage_pct']:.0f}%")
        if gpis.get("key_drivers"):
            with st.expander("Key drivers", expanded=True):
                for d in gpis["key_drivers"]:
                    st.markdown(f"- {d}")
        if gpis.get("state_distribution") is not None:
            st.markdown("**Alignment distribution**")
            st.dataframe(gpis["state_distribution"], use_container_width=True, hide_index=True)
        if gpis.get("per_row") is not None:
            st.markdown("**Per-row outcomes**")
            st.dataframe(gpis["per_row"], use_container_width=True, hide_index=True)
    else:
        st.info(gpis.get("reason", "GPIS unavailable."))


def _render_report_blocks(report):
    for block in report.blocks:
        st.markdown(f"### {block.title}")
        if getattr(block, "headline", None):
            st.markdown(block.headline, unsafe_allow_html=True)
        for p in getattr(block, "paragraphs", []) or []:
            st.markdown(p, unsafe_allow_html=True)
        for c in getattr(block, "callouts", []) or []:
            callout(c)
        for b in getattr(block, "bullets", []) or []:
            st.markdown(f"- {b}")
        current = None
        for label, text in getattr(block, "labeled_bullets", []) or []:
            if label != current:
                current = label
                st.markdown(f"**{label}**")
            st.markdown(f"- {text}")
        for tbl in getattr(block, "tables", []) or []:
            st.markdown(f"**{tbl.title}**")
            df = pd.DataFrame(tbl.rows, columns=tbl.columns)
            st.dataframe(df, use_container_width=True, hide_index=True)
        divider()


# ---------------- Internal Report ----------------
with tab_int:
    if not ws.has_internal():
        st.info("Internal report has not been generated yet. Click **Run Internal** above.")
    else:
        report = ws.internal_report
        st.caption(f"Report ID: `{report.report_id}` · Generated {report.generated_at}")
        pdf = render_internal_pdf(ws, branding=branding) if _HAS_BRANDING else render_internal_pdf(ws)
        st.download_button(
            "📄 Download Internal PDF",
            data=pdf,
            file_name=f"EduPulse_{ws.name.replace(' ', '_')}_Internal.pdf",
            mime="application/pdf",
            type="primary",
            key="ana_dl_internal",
        )
        divider()
        _render_report_blocks(report)

# ---------------- External Report ----------------
with tab_ext:
    if not ws.has_external():
        st.info("External report has not been generated yet. Click **Run External** above.")
    else:
        report = ws.external_report
        st.caption(f"Report ID: `{report.report_id}` · Generated {report.generated_at}")
        callout(
            "External reports omit faculty-level detail, anti-gaming flags, and sensitive "
            "operational findings by design."
        )
        pdf = render_external_pdf(ws, branding=branding) if _HAS_BRANDING else render_external_pdf(ws)
        st.download_button(
            "📄 Download External PDF",
            data=pdf,
            file_name=f"EduPulse_{ws.name.replace(' ', '_')}_External.pdf",
            mime="application/pdf",
            type="primary",
            key="ana_dl_external",
        )
        divider()
        _render_report_blocks(report)

# ---------------- Compare Modes ----------------
with tab_cmp:
    if not (ws.has_internal() and ws.has_external()):
        st.info("Generate both reports to compare them side by side.")
    else:
        ir = ws.internal_report
        er = ws.external_report
        if _HAS_DIFF:
            diff = diff_modes(ir.blocks, er.blocks)
            st.markdown("#### What differs between modes")
            cd1, cd2 = st.columns(2)
            with cd1:
                st.markdown("**Internal-only blocks**")
                if diff["internal_only_blocks"]:
                    for t in diff["internal_only_blocks"]:
                        st.markdown(f"- 🔒 {t}")
                else:
                    st.caption("None.")
            with cd2:
                st.markdown("**External-only blocks**")
                if diff["external_only_blocks"]:
                    for t in diff["external_only_blocks"]:
                        st.markdown(f"- 🌐 {t}")
                else:
                    st.caption("None.")
            divider()

        st.markdown("#### Side-by-side")
        col_i, col_e = st.columns(2)
        with col_i:
            st.markdown("**Internal Report**")
            for b in ir.blocks:
                with st.container(border=True):
                    st.markdown(f"**{b.title}**")
                    if getattr(b, "headline", None):
                        st.markdown(b.headline, unsafe_allow_html=True)
                    for p in (getattr(b, "paragraphs", []) or [])[:2]:
                        st.markdown(p, unsafe_allow_html=True)
                    bullets = getattr(b, "bullets", []) or []
                    tables = getattr(b, "tables", []) or []
                    if bullets:
                        st.markdown(f"_{len(bullets)} bullet(s)_")
                    if tables:
                        st.markdown(f"_{len(tables)} table(s)_")
        with col_e:
            st.markdown("**External Report**")
            for b in er.blocks:
                with st.container(border=True):
                    st.markdown(f"**{b.title}**")
                    if getattr(b, "headline", None):
                        st.markdown(b.headline, unsafe_allow_html=True)
                    for p in (getattr(b, "paragraphs", []) or [])[:2]:
                        st.markdown(p, unsafe_allow_html=True)
                    bullets = getattr(b, "bullets", []) or []
                    tables = getattr(b, "tables", []) or []
                    if bullets:
                        st.markdown(f"_{len(bullets)} bullet(s)_")
                    if tables:
                        st.markdown(f"_{len(tables)} table(s)_")

footer()
