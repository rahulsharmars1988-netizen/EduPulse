from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import math
import streamlit as st


# =========================================================
# CORE THEME / CSS
# =========================================================

def inject_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0b1220;
                --panel: #111827;
                --panel-2: #0f172a;
                --text: #e5e7eb;
                --muted: #94a3b8;
                --line: rgba(148, 163, 184, 0.18);
                --success: #10b981;
                --warn: #f59e0b;
                --danger: #ef4444;
                --info: #3b82f6;
                --shadow: 0 10px 30px rgba(2, 6, 23, 0.18);
                --radius-xl: 22px;
                --radius-lg: 18px;
                --radius-md: 14px;
                --radius-sm: 12px;
            }

            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }

            .ep-hero {
                background:
                    radial-gradient(circle at top right, rgba(59,130,246,0.18), transparent 28%),
                    radial-gradient(circle at left, rgba(16,185,129,0.10), transparent 22%),
                    linear-gradient(135deg, #0f172a 0%, #111827 100%);
                border: 1px solid var(--line);
                border-radius: 24px;
                padding: 1.4rem 1.4rem 1.1rem 1.4rem;
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
            }

            .ep-eyebrow {
                display: inline-block;
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #bfdbfe;
                background: rgba(59,130,246,0.12);
                border: 1px solid rgba(59,130,246,0.22);
                padding: 0.3rem 0.55rem;
                border-radius: 999px;
                margin-bottom: 0.75rem;
            }

            .ep-hero h1 {
                margin: 0;
                font-size: 2rem;
                line-height: 1.15;
                color: white;
                font-weight: 800;
            }

            .ep-hero p {
                margin: 0.55rem 0 0 0;
                color: #cbd5e1;
                font-size: 1rem;
                line-height: 1.55;
                max-width: 920px;
            }

            .ep-section-title {
                font-size: 1.05rem;
                font-weight: 800;
                color: #0f172a;
                margin-top: 0.15rem;
                margin-bottom: 0.4rem;
                letter-spacing: 0.01em;
            }

            .ep-subtle {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.5;
            }

            .ep-card {
                background: white;
                border: 1px solid rgba(15,23,42,0.08);
                border-radius: var(--radius-lg);
                padding: 1rem 1rem 0.95rem 1rem;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            }

            .ep-card-dark {
                background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
                border: 1px solid rgba(148,163,184,0.16);
                color: white;
                border-radius: var(--radius-lg);
                padding: 1rem 1rem 0.95rem 1rem;
                box-shadow: var(--shadow);
            }

            .ep-metric-card {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid rgba(15,23,42,0.08);
                border-radius: 18px;
                padding: 1rem 1rem 0.9rem 1rem;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
                min-height: 138px;
            }

            .ep-metric-label {
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #64748b;
                margin-bottom: 0.5rem;
            }

            .ep-metric-value {
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.05;
                color: #0f172a;
                margin-bottom: 0.35rem;
            }

            .ep-metric-helper {
                font-size: 0.92rem;
                color: #475569;
                line-height: 1.45;
            }

            .ep-pill {
                display: inline-block;
                font-size: 0.72rem;
                font-weight: 800;
                padding: 0.28rem 0.55rem;
                border-radius: 999px;
                letter-spacing: 0.02em;
                border: 1px solid transparent;
                margin-bottom: 0.55rem;
            }

            .ep-pill.success {
                color: #065f46;
                background: rgba(16,185,129,0.14);
                border-color: rgba(16,185,129,0.22);
            }

            .ep-pill.warn {
                color: #92400e;
                background: rgba(245,158,11,0.15);
                border-color: rgba(245,158,11,0.24);
            }

            .ep-pill.danger {
                color: #991b1b;
                background: rgba(239,68,68,0.13);
                border-color: rgba(239,68,68,0.22);
            }

            .ep-pill.info {
                color: #1d4ed8;
                background: rgba(59,130,246,0.13);
                border-color: rgba(59,130,246,0.22);
            }

            .ep-callout {
                border-radius: 16px;
                padding: 0.95rem 1rem;
                border: 1px solid rgba(15,23,42,0.08);
                background: #ffffff;
                box-shadow: 0 6px 18px rgba(15,23,42,0.05);
                margin: 0.35rem 0 0.85rem 0;
            }

            .ep-callout strong {
                display: block;
                margin-bottom: 0.2rem;
                font-size: 0.96rem;
            }

            .ep-callout p {
                margin: 0;
                color: #475569;
                line-height: 1.5;
                font-size: 0.92rem;
            }

            .ep-callout.info {
                border-left: 4px solid var(--info);
            }

            .ep-callout.success {
                border-left: 4px solid var(--success);
            }

            .ep-callout.warn {
                border-left: 4px solid var(--warn);
            }

            .ep-callout.danger {
                border-left: 4px solid var(--danger);
            }

            .ep-divider {
                height: 1px;
                border: 0;
                background: linear-gradient(
                    90deg,
                    rgba(148,163,184,0),
                    rgba(148,163,184,0.35),
                    rgba(148,163,184,0)
                );
                margin: 1rem 0 1rem 0;
            }

            .ep-mini-note {
                color: #64748b;
                font-size: 0.84rem;
                line-height: 1.45;
                margin-top: 0.25rem;
            }

            .ep-framework-row {
                background: white;
                border: 1px solid rgba(15,23,42,0.07);
                border-radius: 14px;
                padding: 0.8rem 0.9rem;
                margin-bottom: 0.65rem;
                box-shadow: 0 6px 16px rgba(15,23,42,0.04);
            }

            .ep-framework-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                margin-bottom: 0.45rem;
            }

            .ep-framework-name {
                font-weight: 700;
                color: #0f172a;
                font-size: 0.96rem;
            }

            .ep-framework-score {
                font-weight: 800;
                color: #0f172a;
                font-size: 0.92rem;
            }

            .ep-bar {
                width: 100%;
                height: 10px;
                border-radius: 999px;
                background: #e2e8f0;
                overflow: hidden;
                position: relative;
            }

            .ep-bar-fill {
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #3b82f6, #10b981);
            }

            .ep-bar-fill.warn {
                background: linear-gradient(90deg, #f59e0b, #f97316);
            }

            .ep-bar-fill.danger {
                background: linear-gradient(90deg, #ef4444, #f97316);
            }

            .ep-footer {
                margin-top: 1.25rem;
                padding-top: 0.9rem;
                color: #64748b;
                font-size: 0.84rem;
                border-top: 1px solid rgba(148,163,184,0.2);
            }

            div[data-testid="stMetric"] {
                background: white;
                border: 1px solid rgba(15,23,42,0.07);
                padding: 0.9rem 0.9rem 0.8rem 0.9rem;
                border-radius: 16px;
                box-shadow: 0 6px 18px rgba(15,23,42,0.04);
            }

            div[data-testid="stMetricLabel"] > div {
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SMALL HELPERS
# =========================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if isinstance(value, str):
            cleaned = value.strip().replace("%", "").replace(",", "")
            if cleaned == "":
                return default
            return float(cleaned)
        return float(value)
    except Exception:
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _fmt_num(value: Any, decimals: int = 1) -> str:
    if value is None:
        return "—"
    try:
        n = float(value)
        if math.isfinite(n):
            if abs(n - round(n)) < 1e-9:
                return f"{int(round(n))}"
            return f"{n:.{decimals}f}"
    except Exception:
        pass
    return str(value)


def _fmt_pct(value: Any, decimals: int = 0) -> str:
    if value is None:
        return "—"
    try:
        n = float(value)
        return f"{n:.{decimals}f}%"
    except Exception:
        return str(value)


def _status_tone(label: Optional[str]) -> str:
    text = (label or "").strip().lower()
    if any(x in text for x in ["strong", "healthy", "high", "good", "ready", "stable"]):
        return "success"
    if any(x in text for x in ["watch", "moderate", "mixed", "medium", "caution"]):
        return "warn"
    if any(x in text for x in ["critical", "low", "weak", "fragile", "risk"]):
        return "danger"
    return "info"


def _score_tone(score: Any) -> str:
    s = _safe_float(score, 0.0)
    if s >= 75:
        return "success"
    if s >= 50:
        return "warn"
    return "danger"


def _confidence_label(score: Any) -> str:
    s = _safe_float(score, 0.0)
    if s >= 80:
        return "High confidence"
    if s >= 60:
        return "Moderate confidence"
    return "Low confidence"


def _state_label(score: Any) -> str:
    s = _safe_float(score, 0.0)
    if s >= 75:
        return "Healthy"
    if s >= 50:
        return "Watchlist"
    return "At Risk"


def _normalize_frameworks(framework_scores: Any) -> Dict[str, float]:
    if framework_scores is None:
        return {}
    if isinstance(framework_scores, dict):
        out: Dict[str, float] = {}
        for k, v in framework_scores.items():
            out[str(k)] = _safe_float(v, 0.0)
        return out

    if isinstance(framework_scores, list):
        out = {}
        for item in framework_scores:
            if isinstance(item, dict):
                name = (
                    item.get("name")
                    or item.get("framework")
                    or item.get("label")
                    or item.get("title")
                )
                score = (
                    item.get("score")
                    if "score" in item
                    else item.get("value")
                )
                if name is not None:
                    out[str(name)] = _safe_float(score, 0.0)
        return out

    return {}


def _pick_lowest_framework(framework_scores: Dict[str, float]) -> tuple[Optional[str], Optional[float]]:
    if not framework_scores:
        return None, None
    name = min(framework_scores, key=lambda k: framework_scores[k])
    return name, framework_scores[name]


# =========================================================
# BASE UI BLOCKS
# =========================================================

def hero(title: str, subtitle: Optional[str] = None, eyebrow: str = "EduPulse") -> None:
    subtitle_html = (
        f"<p>{subtitle}</p>"
        if subtitle
        else "<p>Upload, validate, score, interpret, and present decision-grade institutional intelligence.</p>"
    )
    st.markdown(
        f"""
        <div class="ep-hero">
            <div class="ep-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f'<div class="ep-section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="ep-subtle">{subtitle}</div>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown('<hr class="ep-divider" />', unsafe_allow_html=True)


def callout(
    title: str,
    body: str,
    tone: str = "info",
) -> None:
    tone = tone if tone in {"info", "success", "warn", "danger"} else "info"
    st.markdown(
        f"""
        <div class="ep-callout {tone}">
            <strong>{title}</strong>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer(text: str = "EduPulse • Decision Intelligence Layer") -> None:
    st.markdown(f'<div class="ep-footer">{text}</div>', unsafe_allow_html=True)


# =========================================================
# DECISION INTELLIGENCE BLOCKS
# =========================================================

def render_top_decision_cards(
    state: Optional[str] = None,
    score: Optional[Any] = None,
    confidence: Optional[Any] = None,
    framework_scores: Optional[Any] = None,
    *,
    score_label: str = "Integrated Score",
    confidence_label: str = "Confidence",
) -> None:
    fs = _normalize_frameworks(framework_scores)
    inferred_state = state or _state_label(score)
    inferred_confidence = (
        confidence if isinstance(confidence, str) else _confidence_label(confidence)
    )

    lowest_name, lowest_score = _pick_lowest_framework(fs)
    imbalance_text = (
        f"{lowest_name} is the lowest-scoring framework at {_fmt_num(lowest_score)}"
        if lowest_name is not None
        else "No framework imbalance detected"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        tone = _status_tone(inferred_state)
        st.markdown(
            f"""
            <div class="ep-metric-card">
                <div class="ep-pill {tone}">Decision State</div>
                <div class="ep-metric-value">{inferred_state}</div>
                <div class="ep-metric-helper">Overall operating condition based on current integrated result.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        tone = _score_tone(score)
        st.markdown(
            f"""
            <div class="ep-metric-card">
                <div class="ep-pill {tone}">{score_label}</div>
                <div class="ep-metric-value">{_fmt_num(score)}</div>
                <div class="ep-metric-helper">Composite score reflecting the current non-compensatory evaluation.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        tone = _score_tone(confidence if not isinstance(confidence, str) else (85 if "high" in confidence.lower() else 65 if "moderate" in confidence.lower() else 40))
        st.markdown(
            f"""
            <div class="ep-metric-card">
                <div class="ep-pill {tone}">{confidence_label}</div>
                <div class="ep-metric-value">{inferred_confidence}</div>
                <div class="ep-metric-helper">Reliability level of the current assessment based on available evidence strength.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if lowest_name is not None:
        st.markdown(
            f"""
            <div class="ep-callout warn">
                <strong>Imbalance Highlight</strong>
                <p>{imbalance_text}. This is the main drag on overall decision posture and should be reviewed before broad improvement claims are made.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_framework_imbalance(
    framework_scores: Optional[Any],
    title: str = "Framework Balance",
) -> None:
    fs = _normalize_frameworks(framework_scores)
    if not fs:
        return

    section_title(title, "Quick view of which framework is supporting or pulling down the overall picture.")

    ordered = sorted(fs.items(), key=lambda x: x[1])
    for name, score in ordered:
        width = _clamp(_safe_float(score), 0, 100)
        tone = _score_tone(score)
        fill_class = "danger" if tone == "danger" else "warn" if tone == "warn" else ""
        st.markdown(
            f"""
            <div class="ep-framework-row">
                <div class="ep-framework-top">
                    <div class="ep-framework-name">{name}</div>
                    <div class="ep-framework-score">{_fmt_num(score)}</div>
                </div>
                <div class="ep-bar">
                    <div class="ep-bar-fill {fill_class}" style="width:{width}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_decision_snapshot(
    data: Dict[str, Any],
    *,
    title: str = "Decision Snapshot",
) -> None:
    section_title(title, "Top-line summary for immediate decision reading.")
    render_top_decision_cards(
        state=data.get("state"),
        score=data.get("score"),
        confidence=data.get("confidence"),
        framework_scores=data.get("framework_scores") or data.get("framework_breakdown"),
    )


def render_decision_dashboard(result: Dict[str, Any]) -> None:
    """
    Backward-compatible decision dashboard.

    Accepts flexible keys:
    - state / integrated_state / overall_state
    - score / integrated_score / overall_score
    - confidence / confidence_score / evidence_confidence
    - framework_scores / framework_breakdown / scores_by_framework

    This function only improves presentation and does not change logic.
    """
    if not isinstance(result, dict):
        callout(
            "Decision dashboard unavailable",
            "Result payload is not in expected format, so dashboard rendering was skipped.",
            tone="warn",
        )
        return

    state = (
        result.get("state")
        or result.get("integrated_state")
        or result.get("overall_state")
    )

    score = (
        result.get("score")
        if "score" in result
        else result.get("integrated_score", result.get("overall_score"))
    )

    confidence = (
        result.get("confidence")
        if "confidence" in result
        else result.get("confidence_score", result.get("evidence_confidence"))
    )

    framework_scores = (
        result.get("framework_scores")
        or result.get("framework_breakdown")
        or result.get("scores_by_framework")
        or result.get("frameworks")
    )

    section_title(
        "Decision Intelligence Summary",
        "Read the overall condition first, then see which framework is creating the strongest drag."
    )

    render_top_decision_cards(
        state=state,
        score=score,
        confidence=confidence,
        framework_scores=framework_scores,
    )

    fs = _normalize_frameworks(framework_scores)
    if fs:
        divider()
        render_framework_imbalance(fs, "Imbalance Highlight")

    narrative = (
        result.get("executive_summary")
        or result.get("summary")
        or result.get("decision_summary")
    )
    if narrative:
        divider()
        callout("Executive Read", str(narrative), tone="info")


# =========================================================
# OPTIONAL SAFE DISPLAY HELPERS
# =========================================================

def render_kpi_triplet(
    left_label: str,
    left_value: Any,
    mid_label: str,
    mid_value: Any,
    right_label: str,
    right_value: Any,
) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(left_label, _fmt_num(left_value))
    with c2:
        st.metric(mid_label, _fmt_num(mid_value))
    with c3:
        st.metric(right_label, _fmt_num(right_value))


def render_text_block(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="ep-card">
            <div class="ep-section-title" style="margin-bottom:0.35rem;">{title}</div>
            <div class="ep-subtle" style="color:#475569;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
