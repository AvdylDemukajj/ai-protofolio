import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Ops Agent Command", layout="wide")
st.title("🤖 Service Operations Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.info("⚠️ **Safety Mode Active**\n\nDestructive actions are currently restricted by policy.")
    st.write("Try asking: *'Close ticket TICK-104'* or *'Update TICK-101 to Resolved'*")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Command the agent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking and checking safety policies..."):
            try:
                payload = {
                    "message": prompt,
                    "conversation_history": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                }
                resp = requests.post(f"{API_URL}/chat", json=payload)
                data = resp.json()
                
                response_text = data.get("response", "Error occurred.")
                if data.get("blocked"):
                    st.warning("🛑 **Action Blocked by Guardrails**")
                
                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Connection error: {e}")