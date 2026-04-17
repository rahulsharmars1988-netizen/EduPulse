"""
Shared Streamlit UI components.
"""

from __future__ import annotations

import streamlit as st

from config import APP_NAME, APP_TAGLINE, LOGIC_VERSION, TEMPLATE_VERSION


def inject_css():
    st.markdown(
        """
        <style>
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

        .ep-casebar {
            display: flex; align-items: center; justify-content: space-between;
            gap: 10px; flex-wrap: wrap;
            padding: 10px 14px; border: 1px solid #E2E8F0; border-radius: 10px;
            background: #F8FAFC; margin-bottom: 10px;
        }

        .ep-case-title { font-weight: 700; color: #0F172A; font-size: 15px; }

        .ep-chip, .ep-badge {
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 11.5px; font-weight: 600;
        }

        .ep-scorecard {
            padding: 14px 16px; border: 1px solid #E2E8F0; border-radius: 12px;
            background: #FFFFFF;
        }

        .ep-muted { color: #64748B; font-size: 12px; }
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
        f'<p class="ep-muted">Logic v{LOGIC_VERSION} · Template v{TEMPLATE_VERSION}</p>',
        unsafe_allow_html=True,
    )


def render_ui():
    inject_css()
    hero()
    st.write("EduPulse running successfully 🚀")
    footer()
