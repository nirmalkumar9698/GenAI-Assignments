# 🏛️ Tamil Nadu Government Schemes - Knowledge Graph RAG Chatbot

An enterprise-grade **Knowledge Graph Retrieval-Augmented Generation (KG-RAG)** system built with **LangChain**, **Neo4j AuraDB**, **NetworkX**, and **Streamlit**. 

This system converts unstructured government scheme documents into a structured graph network to perform precise multi-hop reasoning and query answering regarding benefits, eligibility criteria, and required documentation.

---

## 🏗️ Knowledge Graph Architecture & Pipeline

Unlike traditional Vector RAG (which relies purely on text similarity search), Knowledge Graph RAG structures information as nodes (entities) and edges (relationships). This prevents hallucinations when handling structured rules.

[ Raw Scheme Text / HTML ]
│
▼
[ LLM Graph Transformer ]  ──►  Extracts Schema-Bound Nodes & Edges
│
▼
[ Graph Database Storage ] ──►  Neo4j AuraDB (Cloud) / NetworkX (Local)
│
▼
[ Natural Language Query ]  ──►  Translates Question to Cypher Query / Graph Traversal
│
▼
[ LLM Context Synthesis ]  ──►  Generates Precise Answer from Graph Contex

---

## 📌 Graph Schema Definition

The graph strictly enforces the following domain schema:

### Nodes (Entities)
* **`Scheme`**: Name of the official government scheme (e.g., *Pudhumai Penn*).
* **`Department`**: The governing department managing the scheme (e.g., *Social Welfare Department*).
* **`Eligibility`**: Target demographics and rules required to apply.
* **`Benefit`**: Subsidies, financial allowances, or equipment provided.
* **`Document`**: Official identity and land documents required.

### Edges (Relationships)
* `(:Scheme)-[:MANAGED_BY]->(:Department)`
* `(:Scheme)-[:HAS_ELIGIBILITY]->(:Eligibility)`
* `(:Scheme)-[:PROVIDES_BENEFIT]->(:Benefit)`
* `(:Scheme)-[:REQUIRES_DOCUMENT]->(:Document)`

---

## 📂 Project Structure

```text
Knowledge_Graph_RAG/
├── .env                  # Environment keys (Neo4j URI, OpenAI API Key)
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Project Python dependencies
├── inject_step1.py       # Step 1: Ingestion setup & SSL validation
├── inject_step2.py       # Step 2: Entity/Relationship extraction & graph loading
├── query_step3.py       # Step 3: GraphCypherQAChain querying engine
├── networkx_rag.py       # Step 4: Local in-memory NetworkX pipeline alternative
├── app.py                # Step 5: Full Streamlit interactive Chatbot app
└── README.md             # Architecture documentation

🚀 Setup & Execution Guide
1. Prerequisites
Python 3.10+

Neo4j AuraDB Free Instance (neo4j.com/cloud/aura/)

OpenAI API Key

2. Environment Configuration
Create a .env file in the root directory:

OPENAI_API_KEY="your_openai_api_key"
NEO4J_URI="neo4j+s://<your-instance-id>.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_neo4j_aura_password"

3. Installation

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

4. Populate Knowledge Graph
Extract entities and load the graph into Neo4j:

python inject_step2.py

5. Run Streamlit Chatbot
Launch the web interface:
streamlit run kg_app.py