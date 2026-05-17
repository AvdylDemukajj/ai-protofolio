import streamlit as st

def render_upload_zone():
    st.markdown("### Drag & Drop PDF Here")
    return st.file_uploader("Upload", type="pdf", label_visibility="collapsed")