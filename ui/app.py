import os
import time
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- INITIALIZATION FUNCTIONS ---

APP_ICON = "🧠"
AI_AVATAR = "🤖"
USER_AVATAR = "🧑‍💻"

def init_page_settings():
    """Configures page title, icon, and layouts."""
    st.set_page_config(page_title="Confluence RAG Assistant", page_icon=APP_ICON)

def init_session_state():
    """Ensures session storage keys exist for history tracking."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

# --- UI COMPONENTS ---

def render_header():
    """Renders the top bar including a native workspace icon and app title."""
    col1, col2 = st.columns([0.08, 0.92])
    with col1:
        st.write("### 🏢")  
    with col2:
        st.title("Confluence Agentic Assistant")

def render_sidebar():
    """Renders the sidebar with diagnostic tools and reset switches."""
    with st.sidebar:
        st.title("🧠 Settings")
        st.caption(f"Session: {st.session_state.session_id[:8]}")
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

def render_sources(chunks, reranked_docs, message_idx):
    """Renders data references dynamically with unique keys to prevent state collapse."""
    if chunks:
        # Appending unique index ensuring elements persist during interaction loops
        with st.expander("📚 Retrieved Source Chunks", expanded=False):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i}:**")
                # Safely parsing dictionaries or string representations dynamically
                chunk_text = chunk.get('text', str(chunk)) if isinstance(chunk, dict) else str(chunk)
                st.info(chunk_text)
                
    if reranked_docs:
        with st.expander("🎯 Reranked Documents", expanded=False):
            for i, doc in enumerate(reranked_docs, 1):
                st.markdown(f"**Document {i}:**")
                doc_text = doc.get('text', str(doc)) if isinstance(doc, dict) else str(doc)
                st.success(doc_text)

def render_chat_history():
    """Loops through historical sequences and displays past exchanges."""
    for idx, message in enumerate(st.session_state.messages):
        avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_sources(
                    message.get("chunks"), 
                    message.get("reranked_docs"), 
                    message_idx=idx
                )

# --- DATA & STREAMING CONTROLS ---

def fetch_agent_response(prompt):
    """Handles network payloads and processes the API server response dynamically."""
    try:
        base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        payload = {"q": prompt, "thread_id": st.session_state.session_id}
        
        response = requests.post(f"{base_url}/query", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        return {
            "answer": data.get("answer", "No response content found."),
            "chunks": data.get("source_chunks", []),
            "reranked_docs": data.get("reranked_docs", [])
        }
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return {
            "answer": "Sorry, I am unable to connect to the server right now.",
            "chunks": [],
            "reranked_docs": []
        }

def stream_text_animation(full_answer):
    """Generates a typewriter-style animation effect for incoming streams."""
    answer_placeholder = st.empty()
    curr_text = ""
    for char in full_answer:
        curr_text += char
        answer_placeholder.markdown(curr_text + "▌")
        time.sleep(0.005)
    answer_placeholder.markdown(full_answer)

# --- MAIN EXECUTION PIPELINE ---

def main():
    init_page_settings()
    init_session_state()
    render_header()
    render_sidebar()
    render_chat_history()

    # Handle incoming user query events
    if prompt := st.chat_input("Ask about confluence documentation..."):
        # 1. Log & show user inputs
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # 2. Extract answer via external service network blocks
        with st.chat_message("assistant", avatar=AI_AVATAR):
            with st.spinner("Thinking..."):
                result = fetch_agent_response(prompt)

            # 3. Simulate natural typewriter delivery
            stream_text_animation(result["answer"])
            
            # 4. Save to session state *BEFORE* rendering context blocks to lock them in memory
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result["answer"],
                "chunks": result["chunks"],
                "reranked_docs": result["reranked_docs"]
            })
            
            # 5. Display validation telemetry panels cleanly
            render_sources(
                result["chunks"], 
                result["reranked_docs"], 
                message_idx=len(st.session_state.messages) - 1
            )

if __name__ == "__main__":
    main()