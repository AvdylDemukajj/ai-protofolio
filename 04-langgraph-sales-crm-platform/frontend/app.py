import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Sales AI Dashboard", layout="wide")
st.title("🤖 Sales AI Command Center")

st.sidebar.header("Actions")
if st.sidebar.button("Refresh Data"):
    st.rerun()

try:
    st.subheader("Add New Lead")
    with st.form("lead_form"):
        company = st.text_input("Company Name")
        website = st.text_input("Website")
        email = st.text_input("Contact Email")
        submitted = st.form_submit_button("Process with AI")
        
        if submitted:
            if not company:
                st.error("Company name is required")
            else:
                payload = {"company_name": company, "website_url": website, "contact_email": email}
                with st.spinner("AI Agent is researching and drafting..."):
                    resp = requests.post(f"{API_URL}/leads/", json=payload)
                    if resp.status_code == 200:
                        st.success("Lead processed successfully!")
                        st.json(resp.json()['agent_result'])
                    else:
                        st.error(f"Error: {resp.text}")
except Exception as e:
    st.error(f"Could not connect to API: {e}")