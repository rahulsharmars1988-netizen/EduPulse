import streamlit as st
from ui import inject_css, hero, footer

st.set_page_config(page_title="EduPulse", layout="wide")

inject_css()
hero()
st.write("EduPulse loaded. Next step: reconnect the original app flow.")
footer()
