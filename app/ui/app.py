import os
import time
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- PAGE SETUP ---
st.set_page_config(page_title="Confluence RAG Assistant", page_icon="🤖")
st.title("🤖 Confluence Agentic Assistant")

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.title("🧠 Settings")
    st.caption(f"Session: {st.session_state.session_id[:8]}")
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- RENDER HISTORY ---
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- USER INPUT & BACKEND CALL ---
if prompt := st.chat_input("Ask about confluence documentation..."):
    # 1. Append and render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Call your backend server
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                payload = {"q": prompt, "thread_id": st.session_state.session_id}
                
                response = requests.post(f"{base_url}/query", json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                full_answer = data.get("answer", "No response content found.")
                
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
                full_answer = "Sorry, I am unable to connect to the server right now."

        # 3. Stream the final response to the UI
        answer_placeholder = st.empty()
        curr_text = ""
        for char in full_answer:
            curr_text += char
            answer_placeholder.markdown(curr_text + "▌")
            time.sleep(0.005)
        
        answer_placeholder.markdown(full_answer)
        st.session_state.messages.append({"role": "assistant", "content": full_answer})