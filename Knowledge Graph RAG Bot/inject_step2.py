import os
import certifi
from dotenv import load_dotenv

# Import directly from langchain_neo4j to eliminate deprecation warnings & API issues
from langchain_neo4j import Neo4jGraph, LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# 1. Environment Setup
load_dotenv()
os.environ["SSL_CERT_FILE"] = certifi.where()

# 2. Connect to Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 3. Initialize LLM for Extraction
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# 4. Define Graph Schema
allowed_nodes = ["Scheme", "Department", "Eligibility", "Benefit", "Document"]
allowed_relationships = [
    "MANAGED_BY", 
    "HAS_ELIGIBILITY", 
    "PROVIDES_BENEFIT", 
    "REQUIRES_DOCUMENT"
]

llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships
)

# 5. Documents to Ingest
documents = [
    Document(
        page_content="""
        Department: Agriculture Department, Tamil Nadu
        Scheme Name: Chief Minister's Solar Powered Pump Sets Scheme
        Eligibility: Farmers owning land with a valid water source in non-electrified areas.
        Benefits: 70% subsidy for installing 5HP to 10HP solar powered pump sets.
        Documents Required: Aadhaar card, Land ownership certificate (Patta), Bank passbook copy.
        """,
        metadata={"source": "TN_AGRI_01"}
    ),
    Document(
        page_content="""
        Department: Social Welfare and Women Empowerment Department, Tamil Nadu
        Scheme Name: Moovalur Ramamirtham Ammiyar Higher Education Assurance Scheme (Pudhumai Penn)
        Eligibility: Girl students who studied from Class 6 to 12 in Tamil Nadu Government schools.
        Benefits: Monthly financial assistance of Rs. 1,000 deposited directly into bank account.
        Documents Required: School transfer certificate, College admission proof, Aadhaar card.
        """,
        metadata={"source": "TN_SW_01"}
    )
]

print("Extracting Graph Documents using LLM...")
graph_documents = llm_transformer.convert_to_graph_documents(documents)

# 6. Store in Neo4j (Clean call without 'base_entity_id')
print("Writing Graph Data to Neo4j AuraDB...")
graph.add_graph_documents(graph_documents)
print("Successfully loaded knowledge graph into Neo4j AuraDB!")