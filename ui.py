from __future__ import annotations

from typing import Any, Dict, Optional
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
                --muted: #94a3b8;
            }

            .ep-hero {
                background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
                border-radius: 24px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                color: white;
            }

            .ep-eyebrow {
                font-size: 0.75rem;
                font-weight: 700;
                color: #93c5fd;
                margin-bottom: 0.6rem;
            }

            .ep-hero h1 {
                margin: 0;
                font-size: 2rem;
                font-weight: 800;
            }

            .ep-hero p {
                margin-top: 0.5rem;
                color: #cbd5e1;
            }

            .ep-author {
                margin-top: 0.8rem;
                font-size: 0.85rem;
                color: #94a3b8;
            }

            .ep-author a {
                color: #93c5fd;
                text-decoration: none;
            }

            .ep-footer {
                margin-top: 1.5rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(148,163,184,0.2);
                font-size: 0.85rem;
                color: #64748b;
            }

            .ep-section-title {
                font-weight: 800;
                margin-bottom: 0.3rem;
            }

            .ep-subtle {
                color: var(--muted);
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HELPERS
# =========================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except:
        return default


def _fmt_num(value: Any) -> str:
    try:
        return str(round(float(value), 1))
    except:
        return "—"


def _state_label(score: Any) -> str:
    s = _safe_float(score)
    if s >= 75:
        return "Healthy"
    if s >= 50:
        return "Watchlist"
    return "At Risk"


def _confidence_label(score: Any) -> str:
    s = _safe_float(score)
    if s >= 80:
        return "High confidence"
    if s >= 60:
        return "Moderate confidence"
    return "Low confidence"


# =========================================================
# HERO (UPDATED WITH BRANDING)
# =========================================================

def hero(
    title: str,
    subtitle: Optional[str] = None,
    eyebrow: str = "EduPulse",
    *,
    owner: str = "Rahul Sharma",
    email: str = "rahulsharma.rs1988@gmail.com",
    linkedin: str = "https://www.linkedin.com/in/rahulsharma",
) -> None:

    st.markdown(
        f"""
        <div class="ep-hero">
            <div class="ep-eyebrow">{eyebrow}</div>

            <h1>{title}</h1>

            <p>{subtitle or "Decision Intelligence System"}</p>

            <div class="ep-author">
                Created by <strong>{owner}</strong> |
                <a href="mailto:{email}">{email}</a> |
                <a href="{linkedin}" target="_blank">LinkedIn</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# BASIC BLOCKS
# =========================================================

def section_title(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f'<div class="ep-section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="ep-subtle">{subtitle}</div>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown("<hr>", unsafe_allow_html=True)


def callout(title: str, body: str) -> None:
    st.info(f"**{title}** — {body}")


# =========================================================
# DECISION DASHBOARD
# =========================================================

def render_decision_dashboard(result: Dict[str, Any]) -> None:

    score = result.get("score")
    state = result.get("state") or _state_label(score)
    confidence = result.get("confidence") or _confidence_label(score)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("State", state)

    with c2:
        st.metric("Score", _fmt_num(score))

    with c3:
        st.metric("Confidence", confidence)

    if "framework_scores" in result:
        st.markdown("### Framework Breakdown")
        for k, v in result["framework_scores"].items():
            st.progress(min(max(float(v)/100, 0), 1))
            st.caption(f"{k}: {_fmt_num(v)}")


# =========================================================
# FOOTER (UPDATED)
# =========================================================

def footer(
    text: str = "EduPulse • Decision Intelligence Layer",
    *,
    owner: str = "Rahul Sharma",
    email: str = "rahulsharma.rs1988@gmail.com",
    linkedin: str = "https://www.linkedin.com/in/rahulsharma",
    year: str = "2026",
) -> None:

    st.markdown(
        f"""
        <div class="ep-footer">

            <div><strong>{text}</strong></div>

            <div>
                Created by <strong>{owner}</strong> |
                <a href="mailto:{email}">{email}</a>
            </div>

            <div>
                <a href="{linkedin}" target="_blank">LinkedIn</a>
            </div>

            <div style="font-size:0.75rem; color:#94a3b8;">
                © {year} {owner}. All Rights Reserved.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
