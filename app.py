import streamlit as st
from case import build_workspace
from ui import inject_css, hero, footer

st.set_page_config(page_title="EduPulse", layout="wide")

inject_css()
hero()

st.title("Upload Case")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# DEBUG LINE (IMPORTANT)
st.write("File status:", uploaded_file)

if uploaded_file is not None:
    st.success("File received")

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

        ws.run_internal()
        ws.run_external()

        st.subheader("EduPulse Result")

        st.write("Integrated:", ws.integrated)
        st.write("Confidence:", ws.confidence)

footer()
