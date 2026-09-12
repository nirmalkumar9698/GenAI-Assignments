import streamlit as st
from rag_engine import FarmerRAGSystem

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="Indian Farmer AI Assistant",
    page_icon="🌾",
    layout="wide"
)

# 2. Main Title Banner (Single styled instance)
st.markdown(
    """
    <div style="background-color: #1e5631; padding: 18px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 2.2rem;">🌾 Indian Farmer AI Assistant</h1>
        <p style="color: #e8f5e9; margin-top: 6px; font-size: 1.05rem;">
            Your guide for central & state agricultural scheme eligibility, documents, and application processes
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# 3. Load RAG Engine
@st.cache_resource
def load_rag_engine():
    return FarmerRAGSystem()

try:
    rag = load_rag_engine()
except Exception as e:
    st.error(f"Failed to initialize engine. Ensure OPENAI_API_KEY is set in .env file. Error: {e}")
    st.stop()

# 4. Initialize Chat History Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Namaste! I am your AI Farmer Assistant. Ask me anything about Indian agricultural schemes like PM-KISAN, PMFBY, KCC, or state-specific yojanas!"
        }
    ]

# 5. Render Existing Chat Conversation History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Single Input Box for Queries
if user_input := st.chat_input("Type your question here (e.g., How do I apply for PM-KISAN?)...", key="farmer_query_input"):
    # Append & Display User Query
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate & Display Assistant Answer
    with st.chat_message("assistant"):
        with st.spinner("Searching scheme databases and government guidelines..."):
            response = rag.query(user_input)
            st.markdown(response)

    # Append Assistant Response to History
    st.session_state.messages.append({"role": "assistant", "content": response})