import os
import networkx as nx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.prompts import PromptTemplate

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize LLMs
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# 3. Prepare Sample Data
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

# 4. Extract Graph Structure via LLM
print("1. Extracting Entities & Relationships with LLM...")
allowed_nodes = ["Scheme", "Department", "Eligibility", "Benefit", "Document"]
allowed_relationships = ["MANAGED_BY", "HAS_ELIGIBILITY", "PROVIDES_BENEFIT", "REQUIRES_DOCUMENT"]

llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships
)

graph_documents = llm_transformer.convert_to_graph_documents(documents)

# 5. Build NetworkX Graph in Python Memory
print("2. Populating NetworkX Graph in memory...")
G = nx.MultiDiGraph()

for doc in graph_documents:
    # Add Nodes
    for node in doc.nodes:
        G.add_node(node.id, type=node.type)
    # Add Edges
    for rel in doc.relationships:
        G.add_edge(rel.source.id, rel.target.id, relation=rel.type)

print(f"NetworkX Graph created successfully with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges!")

# 6. Graph Retrieval Function (Sub-graph Search)
def retrieve_subgraph_context(query_term: str, graph_obj: nx.MultiDiGraph) -> str:
    """Finds matching nodes using fuzzy matching and extracts local neighborhood triples."""
    matching_nodes = [
        node for node in graph_obj.nodes 
        if query_term.lower() in str(node).lower()
    ]
    
    if not matching_nodes:
        return "No matching entities found in Knowledge Graph."
    
    triples = []
    visited_edges = set()
    
    for start_node in matching_nodes:
        # Get 1-hop outbound and inbound edges
        for u, v, k, data in graph_obj.out_edges(start_node, keys=True, data=True):
            edge_str = f"({u}) -[{data.get('relation', 'RELATED_TO')}]-> ({v})"
            if edge_str not in visited_edges:
                triples.append(edge_str)
                visited_edges.add(edge_str)
                
        for u, v, k, data in graph_obj.in_edges(start_node, keys=True, data=True):
            edge_str = f"({u}) -[{data.get('relation', 'RELATED_TO')}]-> ({v})"
            if edge_str not in visited_edges:
                triples.append(edge_str)
                visited_edges.add(edge_str)

    return "\n".join(triples)

# 7. Answer Generation Chain
QA_TEMPLATE = """Answer the user question using ONLY the provided Knowledge Graph context triples.

Context:
{context}

Question: {question}

Answer:"""

qa_prompt = PromptTemplate(template=QA_TEMPLATE, input_variables=["context", "question"])

def ask_networkx_rag(question: str, keyword: str):
    print(f"\n==========================================")
    print(f"User Query: {question}")
    
    # Step A: Retrieve Context from NetworkX
    context = retrieve_subgraph_context(keyword, G)
    print(f"\nRetrieved Graph Triples:\n{context}\n")
    
    # Step B: LLM Answer Generation
    formatted_prompt = qa_prompt.format(context=context, question=question)
    response = llm.invoke(formatted_prompt)
    print(f"Final Answer:\n{response.content}")

# 8. Test Executions
if __name__ == "__main__":
    ask_networkx_rag(
        question="What are the eligibility criteria for the Pudhumai Penn scheme?",
        keyword="Pudhumai Penn"
    )
    ask_networkx_rag(
        question="What documents are required for the Solar Powered Pump Sets Scheme?",
        keyword="Solar"
    )