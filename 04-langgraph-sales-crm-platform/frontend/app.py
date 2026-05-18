"""Streamlit dashboard for human-in-the-loop lead review."""

import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "")

st.set_page_config(page_title="Sales AI Command Center", layout="wide", page_icon="🤖")

st.title("Sales AI Command Center")
st.caption("LangGraph agent — research, score, draft outreach, human approval")


def api_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def fetch_leads(status: str | None = None) -> list:
    params = {}
    if status and status != "All":
        params["status"] = status
    resp = requests.get(f"{API_URL}/leads/", headers=api_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("New lead")
    with st.form("lead_form"):
        company = st.text_input("Company name *")
        website = st.text_input("Website")
        email = st.text_input("Contact email")
        industry = st.text_input("Industry")
        employees = st.number_input("Employee count", min_value=0, value=50, step=1)
        submitted = st.form_submit_button("Run AI agent", type="primary")

        if submitted:
            if not company.strip():
                st.error("Company name is required.")
            else:
                payload = {
                    "company_name": company.strip(),
                    "website_url": website or None,
                    "contact_email": email or None,
                    "industry": industry or None,
                    "employee_count": int(employees),
                }
                with st.spinner("Agent researching and drafting..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/leads/",
                            json=payload,
                            headers=api_headers(),
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            st.success("Lead processed.")
                            st.json(resp.json())
                        else:
                            st.error(resp.text)
                    except requests.RequestException as exc:
                        st.error(f"API error: {exc}")

with col2:
    st.subheader("Pipeline")
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "pending_review", "approved", "rejected", "qualified", "new", "processing"],
    )
    refresh = st.button("Refresh")

    try:
        leads = fetch_leads(None if status_filter == "All" else status_filter)
        if not leads:
            st.info("No leads found.")
        else:
            df = pd.DataFrame(leads)
            display_cols = [
                c
                for c in ["company_name", "lead_score", "status", "buying_intent", "agent_decision"]
                if c in df.columns
            ]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

            st.markdown("### Review draft")
            options = {
                f"{l['company_name']} ({l['status']}) — score {l.get('lead_score', 'N/A')}": l["id"]
                for l in leads
                if l.get("draft_body")
            }
            if options:
                selected = st.selectbox("Select lead", list(options.keys()))
                lead_id = options[selected]
                detail = next(l for l in leads if l["id"] == lead_id)
                st.markdown(f"**Subject:** {detail.get('draft_subject', '')}")
                st.text_area("Email body", detail.get("draft_body", ""), height=200)
                c1, c2 = st.columns(2)
                if c1.button("Approve", type="primary"):
                    r = requests.post(
                        f"{API_URL}/leads/{lead_id}/approve",
                        headers=api_headers(),
                        timeout=30,
                    )
                    st.success("Approved.") if r.status_code == 200 else st.error(r.text)
                    st.rerun()
                if c2.button("Reject"):
                    r = requests.post(
                        f"{API_URL}/leads/{lead_id}/reject",
                        headers=api_headers(),
                        timeout=30,
                    )
                    st.warning("Rejected.") if r.status_code == 200 else st.error(r.text)
                    st.rerun()
            else:
                st.caption("No drafts available for review.")
    except requests.RequestException as exc:
        st.error(f"Could not reach API at {API_URL}: {exc}")
        st.info("Start stack: docker compose up -d")
