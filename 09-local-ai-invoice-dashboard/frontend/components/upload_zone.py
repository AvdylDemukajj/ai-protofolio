import streamlit as st

def render_upload_zone():
    st.file_uploader("Upload PDF Invoice", type=['pdf'])