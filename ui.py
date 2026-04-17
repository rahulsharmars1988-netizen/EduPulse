"""
Shared Streamlit UI components.

Renders:
- product hero band
- case info bar (case name + mode chip + source file)
- framework score cards
- status badges / mode chips
- footer
"""
from __future__ import annotations

import streamlit as st

from .config import APP_NAME, APP_TAGLINE, LOGIC_VERSION, TEMPLATE_VERSION


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

        /* ====== Section dividers / helpers ====== */
        .ep-muted { color: #64748B; font-size: 12px; }
        .ep-section-title { color: #1E3A8A; font-size: 18px; font-weight: 700; margin: 18px 0 6px 0; }
        .ep-divider {
            border: 0; border-top: 1px solid #E2E8F0; margin: 14px 0;
        }

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


def state_badge(state: str) -> str:
    if state is None:
        state = "—"
    good = {"Resilient", "Stable", "Anabolic", "Strong Alignment",
            "Approximate Alignment", "Thriving", "Healthy"}
    warn = {"Vulnerable", "Transitional", "Undersupply", "Weak Alignment",
            "Oversupply", "Stretched", "Attention Needed"}
    bad = {"Priority Action", "Catabolic", "Mismatch", "Fragile", "Critical",
           "Under Pressure", "In Decline", "Alignment Gap", "At Risk",
           "Capacity Exceeds Visible Demand"}
    if state in good:
        cls = "b-good"
    elif state in warn:
        cls = "b-warn"
    elif state in bad:
        cls = "b-bad"
    else:
        cls = "b-neutral"
    return f'<span class="ep-badge {cls}">{state}</span>'


def mode_chip(mode: str) -> str:
    cls = "c-internal" if mode == "internal" else "c-external"
    return f'<span class="ep-chip {cls}">{mode.upper()}</span>'


def case_bar(ws, extra_html: str = ""):
    """Render the case info bar showing name, source file, scored states, generated reports."""
    generated = []
    if ws.has_internal():
        generated.append(mode_chip("internal"))
    if ws.has_external():
        generated.append(mode_chip("external"))
    gen_html = " ".join(generated) if generated else '<span class="ep-muted">no reports generated</span>'
    left = (
        f'<div class="ep-casebar-left">'
        f'<span class="ep-case-title">{ws.name}</span>'
        f'<span class="ep-case-meta">· {ws.original_filename or "—"}</span>'
        f'<span class="ep-case-meta">· uploaded {ws.uploaded_at}</span>'
        f'</div>'
    )
    right = f'<div>{gen_html} {extra_html}</div>'
    st.markdown(f'<div class="ep-casebar">{left}{right}</div>', unsafe_allow_html=True)


def score_card(col, label: str, score, state: str, hint: str = ""):
    """Render a framework score card into the given Streamlit column."""
    score_str = f"{score:.0f}" if isinstance(score, (int, float)) else "—"
    state_str = state if state else "—"
    html = (
        f'<div class="ep-scorecard">'
        f'<div class="label">{label}</div>'
        f'<div class="score">{score_str}</div>'
        f'<div class="state">{state_str}</div>'
        f'<div class="hint">{hint}</div>'
        f'</div>'
    )
    col.markdown(html, unsafe_allow_html=True)


def callout(text: str):
    st.markdown(f'<div class="ep-callout">{text}</div>', unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="ep-section-title">{text}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="ep-divider"/>', unsafe_allow_html=True)
