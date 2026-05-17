# Project 4: LangGraph Sales Outreach & CRM Automation

## 🚀 Overview
An autonomous sales agent platform built with **LangGraph**, **FastAPI**, and **Streamlit**. The agent researches leads, analyzes intent, drafts personalized emails, and routes them for human approval before sending.

## 🏗️ Architecture
- **Agent Core**: LangGraph state machine (Research -> Strategy -> Draft).
- **API**: FastAPI backend exposing endpoints for lead ingestion.
- **Dashboard**: Streamlit UI for human-in-the-loop approval.
- **Database**: PostgreSQL for lead storage and audit logs.

## 🛠️ How to Run

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY