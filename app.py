import streamlit as st
from case import build_workspace
from ui import inject_css, hero, footer


def render_report_ui(report):
    for block in report.blocks:
        st.markdown(f"## {block.title}")

        if block.headline:
            st.markdown(f"**{block.headline}**", unsafe_allow_html=True)

        for p in block.paragraphs:
            st.markdown(p, unsafe_allow_html=True)

        for c in block.callouts:
            st.info(c)

        for b in block.bullets:
            st.markdown(f"- {b}")

        if block.labeled_bullets:
            current = None
            for label, text in block.labeled_bullets:
                if label != current:
                    current = label
                    st.markdown(f"### {label}")
                st.markdown(f"- {text}")

        for table in block.tables:
            st.markdown(f"### {table.title}")
            st.table(table.rows)


st.set_page_config(page_title="EduPulse", layout="wide")

inject_css()
hero()

st.title("Upload Case")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    ws = build_workspace(
        xls_bytes=file_bytes,
        case_name=uploaded_file.name,
        original_filename=uploaded_file.name
    )

    if not ws.validation.ok:
        st.error("Validation Failed")
        for err in ws.validation.errors:
            st.write(f"- {err}")
    else:
        st.success("Validation Passed")

        st.subheader("Analysis Mode")
        c1, c2, c3 = st.columns(3)

        run_internal = c1.button("Run Internal Analysis")
        run_external = c2.button("Run External Analysis")
        run_both = c3.button("Generate Both")

        st.subheader("Core Result")
        st.json(ws.integrated)
        st.json(ws.confidence)

        if run_internal:
            report = ws.run_internal()
            st.subheader("Internal Report")
            render_report_ui(report)

        if run_external:
            report = ws.run_external()
            st.subheader("External Report")
            render_report_ui(report)

        if run_both:
            internal_report, external_report = ws.run_both()

            st.subheader("Internal Report")
            render_report_ui(internal_report)

            st.subheader("External Report")
            render_report_ui(external_report)

footer()
