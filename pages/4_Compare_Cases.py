"""Compare 2–3 cases side by side."""
import pandas as pd
import streamlit as st

import storage
from comparison import compare_cases
from ui import hero, inject_css, footer, section_title, divider

st.set_page_config(page_title="EduPulse — Compare Cases", page_icon="🔁", layout="wide")
inject_css()
hero("Compare Cases — cross-institution view")

ws_all = storage.all_workspaces()
if len(ws_all) < 2:
    st.info("Upload at least two cases to compare.")
    if st.button("→ Go to Upload Case", use_container_width=True, key="cmp_go_upload"):
        st.switch_page("pages/2_Upload_Case.py")
    footer()
    st.stop()

names = [w.name for w in ws_all]
chosen = st.multiselect(
    "Select 2 or 3 cases",
    options=names,
    default=names[: min(3, len(names))],
    max_selections=3,
)

if len(chosen) < 2:
    st.warning("Select at least two cases.")
    footer()
    st.stop()

chosen_ws = [storage.get_workspace(n) for n in chosen]
result = compare_cases(chosen_ws)

section_title("Summary")
df = result["summary_df"]
st.dataframe(df, use_container_width=True, hide_index=True)

divider()
section_title("Comparative narrative")
st.markdown(result["narrative"], unsafe_allow_html=True)

if result.get("deltas"):
    section_title("Score deltas")
    delta_rows = []
    for label, vals in result["deltas"].items():
        row = {"Comparison": label}
        row.update({k: (f"{v:+.1f}" if v is not None else "—") for k, v in vals.items()})
        delta_rows.append(row)
    st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)

divider()
section_title("Strengths, risks, and actions per case")
cols = st.columns(len(chosen_ws))
for col, w in zip(cols, chosen_ws):
    with col:
        st.markdown(f"### {w.name}")
        st.markdown("**Strengths**")
        for s in (result["strengths"].get(w.name) or ["—"]):
            st.markdown(f"- {s}")
        st.markdown("**Risks**")
        for r in (result["risks"].get(w.name) or ["—"]):
            st.markdown(f"- {r}")
        st.markdown("**Actions**")
        for a in (result["actions"].get(w.name) or ["—"]):
            st.markdown(f"- {a}")

divider()
section_title("Download")
combined_csv = result["summary_df"].to_csv(index=False).encode()
st.download_button(
    "📥 Download comparison CSV",
    data=combined_csv,
    file_name="EduPulse_Comparison.csv",
    mime="text/csv",
    key="cmp_dl_csv",
)

footer()
