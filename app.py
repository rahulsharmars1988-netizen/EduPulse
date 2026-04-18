import streamlit as st
from case import build_workspace
from ui import inject_css, hero, footer

# Optional imports with safe fallback
try:
    from report import render_internal_pdf, render_external_pdf
except Exception:
    render_internal_pdf = None
    render_external_pdf = None

try:
    from branding import BrandingSettings
except Exception:
    BrandingSettings = None

try:
    from template import build_template
except Exception:
    build_template = None


def render_report_ui(report):
    for block in report.blocks:
        st.markdown(f"## {block.title}")

        if block.headline:
            st.markdown(block.headline, unsafe_allow_html=True)

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
            try:
                import pandas as pd
                df = pd.DataFrame(table.rows, columns=table.columns)
                st.dataframe(df, width="stretch")
            except Exception:
                st.table(table.rows)


def get_branding():
    if BrandingSettings is None:
        return None

    return BrandingSettings(
        authorized_signature_name="Rahul Sharma",
        designation="Manager – IQAC",
        institution_name="DBS Global University",
        copyright_owner_name="Rahul Sharma",
    )


st.set_page_config(page_title="EduPulse", layout="wide")

inject_css()
hero()

st.title("Upload Case")

# Template download
if build_template is not None:
    st.subheader("Download Template")
    try:
        template_bytes = build_template()
        st.download_button(
            label="Download Excel Template",
            data=template_bytes,
            file_name="EduPulse_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.warning(f"Template generation is not available yet: {e}")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    # rebuild workspace only if new file uploaded
    current_name = uploaded_file.name
    if (
        "ws" not in st.session_state
        or "ws_filename" not in st.session_state
        or st.session_state.ws_filename != current_name
    ):
        st.session_state.ws = build_workspace(
            xls_bytes=file_bytes,
            case_name=uploaded_file.name,
            original_filename=uploaded_file.name,
        )
        st.session_state.ws_filename = current_name

    ws = st.session_state.ws

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

        branding = get_branding()

        if run_internal:
            report = ws.run_internal()
            st.subheader("Internal Report")
            render_report_ui(report)

            if render_internal_pdf is not None:
                try:
                    internal_pdf = render_internal_pdf(ws, branding=branding)
                    st.download_button(
                        label="Download Internal PDF",
                        data=internal_pdf,
                        file_name=f"{ws.name}_internal_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Internal PDF generation failed: {e}")

        if run_external:
            report = ws.run_external()
            st.subheader("External Report")
            render_report_ui(report)

            if render_external_pdf is not None:
                try:
                    external_pdf = render_external_pdf(ws, branding=branding)
                    st.download_button(
                        label="Download External PDF",
                        data=external_pdf,
                        file_name=f"{ws.name}_external_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"External PDF generation failed: {e}")

        if run_both:
            internal_report, external_report = ws.run_both()

            st.subheader("Internal Report")
            render_report_ui(internal_report)

            if render_internal_pdf is not None:
                try:
                    internal_pdf = render_internal_pdf(ws, branding=branding)
                    st.download_button(
                        label="Download Internal PDF",
                        data=internal_pdf,
                        file_name=f"{ws.name}_internal_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Internal PDF generation failed: {e}")

            st.subheader("External Report")
            render_report_ui(external_report)

            if render_external_pdf is not None:
                try:
                    external_pdf = render_external_pdf(ws, branding=branding)
                    st.download_button(
                        label="Download External PDF",
                        data=external_pdf,
                        file_name=f"{ws.name}_external_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"External PDF generation failed: {e}")

footer()
