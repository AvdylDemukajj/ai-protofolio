import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8008")

st.set_page_config(page_title="InvoiceOps AI", layout="wide", page_icon="🧾")

st.title("🧾 InvoiceOps AI Dashboard")
st.markdown("Privacy-first invoice processing with Local LLM.")

# Sidebar
with st.sidebar:
    st.header("Actions")
    if st.button("Refresh Data"):
        st.rerun()
    st.info("💡 Low confidence (<80%) requires manual review.")

# Fetch Data
try:
    response = requests.get(f"{BACKEND_URL}/invoices")
    invoices = response.json()
except Exception as e:
    st.error(f"Cannot connect to Backend: {e}")
    invoices = []

if invoices:
    df = pd.DataFrame(invoices)
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invoices", len(df))
    pending = len(df[df['status'].isin(['needs_review', 'extracted'])])
    col2.metric("Pending Review", pending)
    approved_val = df[df['status']=='approved']['total'].sum() if 'total' in df.columns else 0
    col3.metric("Approved Value", f"${approved_val:,.2f}")

    st.divider()

    # Tabs
    tab1, tab2 = st.tabs(["📋 Review Queue", "📊 Analytics"])

    with tab1:
        st.subheader("Invoices Requiring Review")
        review_df = df[df['status'].isin(['needs_review', 'extracted'])]
        
        if not review_df.empty:
            for _, row in review_df.iterrows():
                with st.expander(f"**{row['vendor_name']}** - ${row['total']} (Conf: {row['extraction_confidence']:.2%})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Date:** {row['invoice_date']}")
                        st.write(f"**File:** {row['file_name']}")
                    
                    action = st.radio("Action", ["Approve", "Reject"], key=f"act_{row['id']}")
                    comment = st.text_area("Comments", key=f"com_{row['id']}")
                    
                    if st.button("Submit Decision", key=f"btn_{row['id']}"):
                        payload = {
                            "action": "approve" if action == "Approve" else "reject",
                            "reviewer": "current_user",
                            "comments": comment
                        }
                        resp = requests.post(f"{BACKEND_URL}/invoices/{row['id']}/review", params=payload)
                        if resp.status_code == 200:
                            st.success("Decision recorded!")
                            st.rerun()
                        else:
                            st.error("Failed to save.")
        else:
            st.success("✅ No pending reviews!")

    with tab2:
        st.subheader("Financial Overview")
        if not df.empty and 'total' in df.columns:
            fig = px.bar(df, x='vendor_name', y='total', color='status', title="Spend by Vendor")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No invoices found. Upload one via API or wait for ingestion.")