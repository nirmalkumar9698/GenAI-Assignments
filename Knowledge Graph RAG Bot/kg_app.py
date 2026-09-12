import os
import certifi
import streamlit as st
from dotenv import load_dotenv

from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# -----------------------------------------------------------------------------
# 1. Environment & Database Configuration
# -----------------------------------------------------------------------------
load_dotenv()
os.environ["SSL_CERT_FILE"] = certifi.where()

st.set_page_config(
    page_title="TN Govt Schemes Knowledge Graph RAG",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ TN Government Schemes - Knowledge Graph Chatbot")
st.markdown("Ask questions about eligibility, benefits, and required documents for Tamil Nadu government schemes.")

@st.cache_resource
def init_graph_chain():
    """Initializes and caches the Neo4j Graph Connection & Cypher QA Chain."""
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    graph.refresh_schema()

    # Custom Cypher Generator Prompt
    cypher_template = """
    Task: Generate Cypher statement to query a Neo4j graph database.
    Schema:
    {schema}

    CRITICAL RULES:
    1. Use `TOLOWER(n.id) CONTAINS TOLOWER('...')` for string matching.
    2. Search using flexible partial keywords for Scheme names and Benefits.
    3. Return descriptive column aliases: `RETURN s.id AS scheme, d.id AS department, e.id AS eligibility, b.id AS benefit, doc.id AS document`.

    Question: {question}
    Cypher Statement:"""

    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=cypher_template
    )

    # Custom QA Prompt
    qa_template = """You are an AI assistant answering questions about Tamil Nadu Government Schemes using context from a Knowledge Graph.

    Graph Context:
    {context}

    User Question: {question}

    Provide a clear, well-formatted, and helpful response:"""

    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=qa_template
    )

    cypher_llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    qa_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

    chain = GraphCypherQAChain.from_llm(
        graph=graph,
        cypher_llm=cypher_llm,
        qa_llm=qa_llm,
        cypher_prompt=cypher_prompt,
        qa_prompt=qa_prompt,
        verbose=True,
        allow_dangerous_requests=True
    )
    return chain

# Initialize Chain
try:
    qa_chain = init_graph_chain()
    st.sidebar.success("Connected to Neo4j Knowledge Graph!")
except Exception as e:
    st.sidebar.error(f"Failed to connect to Neo4j: {e}")
    st.stop()

# Sidebar Information
st.sidebar.header("Sample Queries")
st.sidebar.markdown("""
- *What are the eligibility criteria for the Pudhumai Penn scheme?*
- *What documents are needed for the Solar Powered Pump Sets scheme?*
- *Which department manages the Pudhumai Penn scheme?*
""")

# -----------------------------------------------------------------------------
# 2. Chat Memory & UI Handling
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me anything about Tamil Nadu Government Schemes."}
    ]

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input Prompt
if user_query := st.chat_input("Type your question here..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # Generate Response from Graph RAG
    with st.chat_message("assistant"):
        with st.spinner("Searching Knowledge Graph..."):
            try:
                response = qa_chain.invoke({"query": user_query})
                answer = response["result"]
            except Exception as err:
                answer = f"Sorry, I couldn't query the graph for this question. Error: {err}"
            
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})