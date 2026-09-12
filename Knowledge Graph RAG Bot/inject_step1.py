import os
import certifi
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Use updated package to resolve deprecation warnings
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document

# 1. Load environment variables
load_dotenv()

# Set Python's global SSL certificate path (helps on Windows)
os.environ["SSL_CERT_FILE"] = certifi.where()

# 2. Connect to Neo4j Aura DB
try:
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    print("Successfully connected to Neo4j Aura DB!")
except Exception as e:
    print(f"Connection error details: {e}")
    # Fallback attempt if SSL strict check fails on Windows network
    print("Retrying connection with enhanced SSL configuration...")
    import neo4j
    driver = neo4j.GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
        trusted_certificates=neo4j.TrustSystemCAs()
    )
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        driver_config={"trusted_certificates": neo4j.TrustSystemCAs()}
    )
    print("Successfully connected to Neo4j Aura DB on retry!")

# 3. Data Collection / Parsing Function
def get_tn_schemes_data():
    url = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
            return [Document(page_content=content[:4000], metadata={"source": url})]
    except Exception as e:
        print(f"Web fetch failed ({e}). Proceeding with sample data.")

    # Sample Data mimicking TN Govt Agriculture & Welfare Schemes
    sample_docs = [
        Document(
            page_content="""
            Department: Agriculture Department, Tamil Nadu
            Scheme Name: Chief Minister's Solar Powered Pump Sets Scheme
            Eligibility: Farmers owning land with a valid water source in non-electrified areas.
            Benefits: 70% subsidy for installing 5HP to 10HP solar powered pump sets.
            Documents Required: Aadhar card, Land ownership certificate (Patta), Bank passbook copy.
            """,
            metadata={"department": "Agriculture", "scheme_id": "TN_AGRI_01"}
        ),
        Document(
            page_content="""
            Department: Social Welfare and Women Empowerment Department, Tamil Nadu
            Scheme Name: Moovalur Ramamirtham Ammiyar Higher Education Assurance Scheme (Pudhumai Penn)
            Eligibility: Girl students who studied from Class 6 to 12 in Tamil Nadu Government schools.
            Benefits: Monthly financial assistance of Rs. 1,000 deposited directly into the student's bank account.
            Documents Required: School transfer certificate, College admission proof, Aadhar card.
            """,
            metadata={"department": "Social Welfare", "scheme_id": "TN_SW_01"}
        )
    ]
    return sample_docs

documents = get_tn_schemes_data()
print(f"Loaded {len(documents)} document(s) ready for Entity Extraction.")