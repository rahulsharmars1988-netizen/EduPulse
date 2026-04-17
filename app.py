import streamlit as st

from case import CaseWorkspace
from ui import inject_css, hero, footer

st.set_page_config(page_title="EduPulse", layout="wide")

inject_css()
hero()

st.title("Upload Case")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    st.success("File uploaded successfully")
    st.write("Next: connect scoring engine")

footer()
