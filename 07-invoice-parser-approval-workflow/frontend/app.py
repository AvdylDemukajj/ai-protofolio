import streamlit as st
import requests
import os
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Invoice Approval Center", layout="wide")

st.title("🧾 Invoice Approval Center")
st.markdown("Review AI-extracted invoices and approve or reject them.")

# Sidebar Upload
with st.sidebar:
    st.header("Upload New Invoice")
    uploaded_file = st.file_uploader("Choose PDF", type="pdf")
    if uploaded_file and st.button("Upload & Process"):
        with st.spinner("Processing..."):
            files = {"file": uploaded_file.getvalue()}
            # Note: In real streamlit file upload, we need to send as multipart properly
            # Simplified for demo logic
            try:
                resp = requests.post(f"{BACKEND_URL}/upload", files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")})
                if resp.status_code == 200:
                    st.success("Uploaded successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

# Main Table
try:
    resp = requests.get(f"{BACKEND_URL}/invoices")
    if resp.status_code == 200:
        data = resp.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Filter for reviews
            review_df = df[df['status'].isin(['needs_review', 'processed'])]
            
            if not review_df.empty:
                st.subheader("Pending Reviews")
                for _, row in review_df.iterrows():
                    with st.expander(f"**{row['vendor']}** - ${row['total']} (Confidence: {row['confidence']:.2%})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {row['id'][:8]}...")
                            st.write(f"**Status:** {row['status']}")
                        with col2:
                            st.write(f"**Date:** {row['date']}")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✅ Approve", key=f"app_{row['id']}"):
                                requests.post(f"{BACKEND_URL}/invoices/{row['id']}/review", params={"action": "approve", "reviewer": "user"})
                                st.rerun()
                        with c2:
                            if st.button("❌ Reject", key=f"rej_{row['id']}"):
                                requests.post(f"{BACKEND_URL}/invoices/{row['id']}/review", params={"action": "reject", "comments": "Manual reject", "reviewer": "user"})
                                st.rerun()
            else:
                st.success("✅ All caught up! No pending reviews.")
        else:
            st.info("No invoices found.")
except Exception as e:
    st.error(f"Could not connect to backend: {e}")