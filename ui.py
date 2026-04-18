"""
Shared Streamlit UI components.

Renders:
- product hero band
- case info bar (case name + mode chip + source file)
- framework score cards
- status badges / mode chips
- footer
- decision intelligence dashboard (snapshot, score cards,
  framework bars, balance summary, risk box, timeline)

All dashboard functions are defensive: missing keys, None values, and
partial data never raise. Streamlit-only, no external plotting libraries.
"""
from __future__ import annotations

from typing import Any, Optional, Dict, List
import streamlit as st

from config import APP_NAME, APP_TAGLINE, LOGIC_VERSION, TEMPLATE_VERSION


# ===========================================================================
# CSS / chrome
# ===========================================================================
def inject_css():
    st.markdown(
        """
        <style>
        /* ====== Hero ====== */
        .ep-hero {
            padding: 22px 24px;
            border-radius: 16px;
            background: linear-gradient(135deg, #0B1F5C 0%, #1E3A8A 45%, #4338CA 100%);
            color: white;
            margin-bottom: 16px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        }
        .ep-hero h1 {
            color: white; margin: 0; font-size: 28px;
            letter-spacing: -0.4px; font-weight: 700;
        }
        .ep-hero p {
            color: #CBD5E1; margin: 4px 0 0 0; font-size: 13px;
        }

        /* ====== Case info bar ====== */
        .ep-casebar {
            display: flex; align-items: center; justify-content: space-between;
            gap: 10px; flex-wrap: wrap;
            padding: 10px 14px; border: 1px solid #E2E8F0; border-radius: 10px;
            background: #F8FAFC; margin-bottom: 10px;
        }
        .ep-casebar-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .ep-case-title { font-weight: 700; color: #0F172A; font-size: 15px; }
        .ep-case-meta  { color: #64748B; font-size: 12px; }

        /* ====== Badges / chips ====== */
        .ep-chip, .ep-badge {
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 11.5px; font-weight: 600;
            letter-spacing: 0.2px;
        }
        .ep-chip { font-size: 11px; }
        .b-good    { background: #DCFCE7; color: #166534; }
        .b-warn    { background: #FEF3C7; color: #92400E; }
        .b-bad     { background: #FEE2E2; color: #991B1B; }
        .b-neutral { background: #E0E7FF; color: #1E3A8A; }
        .c-internal { background: #DBEAFE; color: #1E40AF; }
        .c-external { background: #EDE9FE; color: #5B21B6; }

        /* ====== Score cards ====== */
        .ep-scorecard {
            padding: 14px 16px; border: 1px solid #E2E8F0; border-radius: 12px;
            background: #FFFFFF; height: 100%;
        }
        .ep-scorecard .label { color: #64748B; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
        .ep-scorecard .score { font-size: 30px; font-weight: 800; color: #0F172A; line-height: 1.1; margin: 4px 0; }
        .ep-scorecard .state { color: #1E3A8A; font-weight: 600; font-size: 13px; }
        .ep-scorecard .hint  { color: #64748B; font-size: 11.5px; margin-top: 6px; }

        /* ====== Section helpers ====== */
        .ep-muted { color: #64748B; font-size: 12px; }
        .ep-section-title { color: #1E3A8A; font-size: 18px; font-weight: 700; margin: 18px 0 6px 0; }
        .ep-divider { border: 0; border-top: 1px solid #E2E8F0; margin: 14px 0; }

        /* ====== Callout ====== */
        .ep-callout {
            padding: 10px 14px; border-left: 3px solid #1E3A8A;
            background: #F1F5F9; border-radius: 4px; margin: 8px 0;
            font-size: 13px; color: #0F172A;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(subtitle: str | None = None):
    sub = subtitle or APP_TAGLINE
    st.markdown(
        f'<div class="ep-hero"><h1>{APP_NAME}</h1><p>{sub}</p></div>',
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        f'<p class="ep-muted">Logic v{LOGIC_VERSION} · Template v{TEMPLATE_VERSION} · '
        f'Diagnostic tool — not a ranking, compliance, or accreditation instrument.</p>',
        unsafe_allow_html=True,
    )


def callout(text: str):
    st.markdown(f'<div class="ep-callout">{text}</div>', unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="ep-section-title">{text}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="ep-divider"/>', unsafe_allow_html=True)


# ===========================================================================
# Dashboard helpers (merged from ui_components.py)
# ===========================================================================
def _safe_num(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        f = float(value)
        if f != f:  # NaN
            return None
        return f
    except (TypeError, ValueError):
        return None


def _fmt_score(value: Any, decimals: int = 1) -> str:
    n = _safe_num(value)
    if n is None:
        return "—"
    return f"{n:.{decimals}f}"


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _state_tone(state: Optional[str]) -> str:
    if not state:
        return "•"
    positive = {"Thriving", "Healthy", "Resilient", "Stable", "Anabolic",
                "Strong Alignment", "Approximate Alignment"}
    warning = {"Stretched", "Attention Needed", "Vulnerable", "Transitional",
               "Undersupply", "Weak Alignment", "Oversupply"}
    critical = {"At Risk", "Fragile", "Critical", "Priority Action",
                "Catabolic", "Mismatch", "Under Pressure", "In Decline",
                "Alignment Gap", "Capacity Exceeds Visible Demand"}
    if state in positive:
        return "🟢"
    if state in warning:
        return "🟡"
    if state in critical:
        return "🔴"
    return "⚪"


# ===========================================================================
# Dashboard renderers
# ===========================================================================
def render_score_card(title: str, score: Any, state: Optional[str] = None,
                      confidence: Optional[str] = None, help_text: Optional[str] = None) -> None:
    """Render a top-level KPI card with score, optional state and confidence."""
    if not title:
        title = "Score"
    score_str = _fmt_score(score)
    with st.container(border=True):
        st.markdown(f"**{title}**")
        try:
            st.metric(label=" ", value=score_str, label_visibility="collapsed")
        except Exception:
            st.markdown(f"### {score_str}")
        if state:
            st.markdown(f"{_state_tone(state)} **{state}**")
        if confidence:
            st.markdown(
                f"<span style='color:#64748B;font-size:12px;'>Confidence: {confidence}</span>",
                unsafe_allow_html=True,
            )
        if help_text:
            st.caption(help_text)


def render_framework_bar(name: str, score: Any, state: Optional[str] = None,
                          weight: Optional[float] = None) -> None:
    """Render a single framework as a labelled progress bar."""
    display_name = name if name else "Framework"
    num = _safe_num(score)

    header_bits = [f"**{display_name}**"]
    if num is None:
        header_bits.append("<span style='color:#94A3B8;'>No data</span>")
    else:
        header_bits.append(f"<span style='font-weight:600;'>{num:.1f}/100</span>")
    if state:
        header_bits.append(f"{_state_tone(state)} {state}")
    if weight is not None:
        w_num = _safe_num(weight)
        if w_num is not None:
            header_bits.append(
                f"<span style='color:#64748B;font-size:12px;'>weight {w_num:.0%}</span>"
            )

    st.markdown(" &nbsp; · &nbsp; ".join(header_bits), unsafe_allow_html=True)
    if num is None:
        st.progress(0.0)
    else:
        st.progress(_clamp(num) / 100.0)


def render_risk_box(risks: Optional[List[str]]) -> None:
    """Render critical risks block. Empty/None → low-risk message."""
    with st.container(border=True):
        st.markdown("### ⚠ Critical Risks")
        if not risks:
            st.success("No critical risks surface at this time.")
            return
        if not isinstance(risks, (list, tuple)):
            risks = [str(risks)]
        for r in risks:
            if r is None:
                continue
            st.markdown(f"- {r}")


def render_timeline(timeline_projection: Optional[Dict[str, str]]) -> None:
    """Render three-column forward outlook: 0-3, 3-6, 6-12 months."""
    if not isinstance(timeline_projection, dict):
        timeline_projection = {}

    headings = [("0–3 months", "0_3_months"),
                ("3–6 months", "3_6_months"),
                ("6–12 months", "6_12_months")]

    st.markdown("### 🗓 Timeline Projection")
    cols = st.columns(3)
    for col, (label, key) in zip(cols, headings):
        with col:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                text = timeline_projection.get(key) if isinstance(timeline_projection, dict) else None
                st.markdown(text if text else "_No projection available._")


def render_system_snapshot(snapshot: Optional[Dict[str, Any]]) -> None:
    """Render the top-of-dashboard snapshot card."""
    if not isinstance(snapshot, dict):
        snapshot = {}

    state = snapshot.get("state") or "—"
    score = snapshot.get("score")
    confidence = snapshot.get("confidence") or "—"
    status_line = snapshot.get("status_line") or ""

    with st.container(border=True):
        st.markdown("### 🩺 System Snapshot")
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            st.markdown(f"{_state_tone(state)} **{state}**")
            if status_line:
                st.caption(status_line)
        with c2:
            st.metric("Score", _fmt_score(score))
        with c3:
            st.metric("Confidence", str(confidence))


def render_balance_summary(balance_analysis: Optional[Dict[str, Any]],
                            priority_focus: Optional[str] = None) -> None:
    """Render strongest/weakest frameworks, insight, and optional priority focus."""
    if not isinstance(balance_analysis, dict):
        balance_analysis = {}

    strongest = balance_analysis.get("strongest_framework")
    weakest = balance_analysis.get("weakest_framework")
    insight = balance_analysis.get("insight") or "Insufficient data for balance analysis."

    with st.container(border=True):
        st.markdown("### ⚖ Balance Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Strongest framework**")
            st.markdown(
                f"<span style='font-size:18px;font-weight:600;color:#166534;'>{strongest or '—'}</span>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown("**Weakest framework**")
            st.markdown(
                f"<span style='font-size:18px;font-weight:600;color:#991B1B;'>{weakest or '—'}</span>",
                unsafe_allow_html=True,
            )
        st.markdown("")
        st.markdown(f"_{insight}_")
        if priority_focus:
            st.markdown(
                f"<div style='padding:8px 12px;border-left:3px solid #1E3A8A;"
                f"background:#F1F5F9;border-radius:4px;margin-top:6px;'>"
                f"<b>Priority focus:</b> {priority_focus}</div>",
                unsafe_allow_html=True,
            )


def render_framework_section(integrated: Optional[Dict[str, Any]]) -> None:
    """Render ICG / DMM / GPIS framework bars from integrated['contributions']."""
    if not isinstance(integrated, dict):
        integrated = {}
    contributions = integrated.get("contributions") or {}

    with st.container(border=True):
        st.markdown("### 📊 Framework Performance")
        if not contributions:
            st.info("No framework contributions available yet.")
            return
        for fw in ("ICG", "DMM", "GPIS"):
            entry = contributions.get(fw) if isinstance(contributions, dict) else None
            if entry is None:
                render_framework_bar(fw, None)
                st.markdown("")
                continue
            render_framework_bar(
                name=fw,
                score=entry.get("score"),
                state=entry.get("state"),
                weight=entry.get("weight"),
            )
            st.markdown("")


# ===========================================================================
# Intelligence derivation (fallback-safe)
# ===========================================================================
def _derive_snapshot_from_case(case) -> Dict[str, Any]:
    try:
        from edupulse.report_compose import build_system_snapshot
        return build_system_snapshot(case) or {}
    except Exception:
        pass
    try:
        from report_compose import build_system_snapshot
        return build_system_snapshot(case) or {}
    except Exception:
        pass
    integ = getattr(case, "integrated", None) or {}
    conf_obj = getattr(case, "confidence", None) or {}
    return {
        "state": integ.get("state"),
        "score": integ.get("score"),
        "confidence": conf_obj.get("label"),
        "status_line": "",
    }


def _derive_balance_from_case(case) -> Dict[str, Any]:
    try:
        from edupulse.report_compose import build_balance_analysis
        return build_balance_analysis(case) or {}
    except Exception:
        pass
    try:
        from report_compose import build_balance_analysis
        return build_balance_analysis(case) or {}
    except Exception:
        pass
    scores = {}
    for name, res in [("ICG", getattr(case, "icg", None)),
                      ("DMM", getattr(case, "dmm", None)),
                      ("GPIS", getattr(case, "gpis", None))]:
        if isinstance(res, dict) and res.get("available") and res.get("score") is not None:
            scores[name] = float(res["score"])
    if not scores:
        return {"strongest_framework": None, "weakest_framework": None,
                "insight": "Insufficient framework data for balance analysis."}
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)
    return {"strongest_framework": strongest, "weakest_framework": weakest,
            "insight": f"Performance is driven by {strongest}; constrained by {weakest}."}


def _derive_priority_from_case(case) -> Optional[str]:
    try:
        from edupulse.report_compose import build_priority_focus
        return build_priority_focus(case)
    except Exception:
        pass
    try:
        from report_compose import build_priority_focus
        return build_priority_focus(case)
    except Exception:
        return None


def _derive_risks_from_case(case) -> List[str]:
    try:
        from edupulse.report_compose import build_risk_highlights
        return build_risk_highlights(case) or []
    except Exception:
        pass
    try:
        from report_compose import build_risk_highlights
        return build_risk_highlights(case) or []
    except Exception:
        return []


def _derive_timeline_from_case(case) -> Dict[str, str]:
    try:
        from edupulse.report_compose import build_timeline_projection
        return build_timeline_projection(case) or {}
    except Exception:
        pass
    try:
        from report_compose import build_timeline_projection
        return build_timeline_projection(case) or {}
    except Exception:
        return {}


# ===========================================================================
# Master dashboard renderer
# ===========================================================================
def render_decision_dashboard(case) -> None:
    """
    Master renderer. Accepts the full case/workspace object and assembles
    the decision dashboard. Degrades gracefully if any sub-object is missing.
    """
    if case is None:
        st.info("No case to display.")
        return

    integ = getattr(case, "integrated", None) or {}
    conf_obj = getattr(case, "confidence", None) or {}

    # --- Row 1: snapshot
    snapshot = _derive_snapshot_from_case(case)
    render_system_snapshot(snapshot)

    # --- Row 2: headline KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_score_card(
            title="EduPulse Score",
            score=integ.get("score"),
            state=integ.get("state"),
            confidence=conf_obj.get("label"),
            help_text="Weighted integrated score across ICG, DMM, GPIS.",
        )
    with c2:
        icg = getattr(case, "icg", None) or {}
        render_score_card(
            title="ICG · Continuity",
            score=icg.get("score"),
            state=icg.get("state"),
            help_text=f"{icg.get('faculty_count', 0)} faculty rows" if icg.get("available") else None,
        )
    with c3:
        dmm = getattr(case, "dmm", None) or {}
        progs = 0
        try:
            progs = len(dmm.get("programme_table", []))
        except Exception:
            progs = 0
        render_score_card(
            title="DMM · Vitality",
            score=dmm.get("score"),
            state=dmm.get("state"),
            help_text=f"{progs} programmes" if dmm.get("available") else None,
        )
    with c4:
        gpis = getattr(case, "gpis", None) or {}
        rows = 0
        try:
            rows = len(gpis.get("per_row", []))
        except Exception:
            rows = 0
        render_score_card(
            title="GPIS · Alignment",
            score=gpis.get("score"),
            state=gpis.get("state"),
            help_text=f"{rows} supply rows" if gpis.get("available") else None,
        )

    st.markdown("")

    # --- Row 3: framework bars + balance
    left, right = st.columns([1, 1])
    with left:
        render_framework_section(integ)
    with right:
        balance = _derive_balance_from_case(case)
        priority = _derive_priority_from_case(case)
        render_balance_summary(balance, priority_focus=priority)

    st.markdown("")

    # --- Row 4: risks + timeline
    risks = _derive_risks_from_case(case)
    render_risk_box(risks)

    st.markdown("")
    timeline = _derive_timeline_from_case(case)
    render_timeline(timeline)
