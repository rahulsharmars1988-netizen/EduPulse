import streamlit as st

from ui import render_ui  # assuming Claude ne UI yaha banaya hai

st.set_page_config(page_title="EduPulse", layout="wide")

def main():
    render_ui()

if __name__ == "__main__":
    main()
