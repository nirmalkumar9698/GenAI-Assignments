import os
import certifi
from dotenv import load_dotenv

from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. Environment Setup
load_dotenv()
os.environ["SSL_CERT_FILE"] = certifi.where()

# 2. Connect to Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

graph.refresh_schema()

# 3. Custom Cypher Generation Prompt
CYPHER_GENERATION_TEMPLATE = """
Task: Generate Cypher statement to query a Neo4j graph database.
Instructions:
Use only the provided schema elements (nodes, relationships, properties).

Schema:
{schema}

CRITICAL RULES:
1. Use `TOLOWER(n.id) CONTAINS TOLOWER('...')` for string matching on node IDs.
2. For benefits or indirect questions (e.g., "financial support" or "girl students"), match on the Scheme node name first, or use flexible partial string matching across related nodes.
3. Return simple column aliases like `RETURN s.id AS scheme, d.id AS department, e.id AS eligibility, b.id AS benefit, doc.id AS document`.

Question: {question}
Cypher Statement:"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

# 4. Custom QA Prompt (Ensures the LLM reads Cypher dictionary output properly)
QA_TEMPLATE = """You are a helpful assistant answering questions using information from a Knowledge Graph.

Context from Neo4j Graph Database:
{context}

Question: {question}

Helpful Answer:"""

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)

# 5. Initialize Chain
cypher_llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
qa_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=cypher_llm,
    qa_llm=qa_llm,
    cypher_prompt=CYPHER_PROMPT,
    qa_prompt=QA_PROMPT,
    verbose=True,
    allow_dangerous_requests=True
)

def ask_kg_rag(question: str):
    print(f"\n==========================================")
    print(f"User Query: {question}")
    result = chain.invoke({"query": question})
    print(f"\nFinal Answer:\n{result['result']}\n")

if __name__ == "__main__":
    ask_kg_rag("What are the eligibility criteria for the Pudhumai Penn scheme?")
    ask_kg_rag("What documents are required for the Solar Powered Pump Sets Scheme?")
    ask_kg_rag("Which department manages the Pudhumai Penn scheme?")