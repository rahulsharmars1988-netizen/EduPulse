"""Download the official EduPulse template (and optional sample cases)."""
import streamlit as st

from template import template_bytes
try:
    from samples import sample_case_bytes, sample_case_v2_bytes
    _HAS_SAMPLES = True
except Exception:
    _HAS_SAMPLES = False

from ui import hero, inject_css, footer, section_title, divider

st.set_page_config(page_title="EduPulse — Download Template", page_icon="📥", layout="wide")
inject_css()
hero("Download the official EduPulse template")

st.write(
    "The master workbook contains four input sheets "
    "(**ICG_Input**, **DMM_Input**, **GPIS_Supply**, **GPIS_Demand**) plus a README. "
    "Dropdown validation is built in. Do not rename sheets or column headers."
)

if _HAS_SAMPLES:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Download blank template",
            data=template_bytes(),
            file_name="EduPulse_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
    with col2:
        st.download_button(
            label="🧪 Sample case — stressed",
            data=sample_case_bytes(),
            file_name="EduPulse_SampleCase_Stressed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Pre-filled workbook showing succession pressure and weak alignment.",
        )
    with col3:
        st.download_button(
            label="🧪 Sample case — healthy",
            data=sample_case_v2_bytes(),
            file_name="EduPulse_SampleCase_Healthy.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Pre-filled workbook showing a resilient, well-aligned institution.",
        )
else:
    st.download_button(
        label="📥 Download blank template",
        data=template_bytes(),
        file_name="EduPulse_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary",
    )

divider()
section_title("Template structure")
st.markdown(
    "- **ICG_Input** — one row per faculty member.\n"
    "- **DMM_Input** — one row per programme.\n"
    "- **GPIS_Supply** — one row per programme × domain × geography.\n"
    "- **GPIS_Demand** — one row per domain × geography.\n"
    "- **LOOKUPS** — hidden helper sheet used for dropdowns."
)
st.caption(
    "Scoring happens entirely in the EduPulse engine. Do not add formulas to the workbook — "
    "the engine owns the logic and the Excel file is strictly an input carrier."
)

footer()
