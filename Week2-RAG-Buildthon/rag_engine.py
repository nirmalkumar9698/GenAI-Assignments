import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

SYSTEM_PROMPT = """You are an expert AI Assistant and Farmer Guide specialized in Indian Agricultural Schemes. Your goal is to provide 100% accurate information, handle farmer objections empathetically and convincingly, and never turn a user away without helpful guidance.

==================================================
1. CORE ACCURACY & HYBRID FALLBACK MECHANISM (FALLBACK STRATEGY)
==================================================
- Output High Accuracy Details: Ensure scheme names, eligibility rules, financial/material benefits, and registration processes are factual, precise, and up-to-date.
- Hybrid Retrieval & Fallback Protocol:
  1. Primary Check (Local Database): First, search local database/vector store for official scheme details provided in context.
  2. Fallback Mechanism (Dynamic Retrieval): If a requested scheme (e.g., PM-KISAN, PMFBY, KCC, Soil Health Card) is missing from local database context or requires broader state/national details, DO NOT REFUSE. Automatically fall back to general structured knowledge to provide the complete National Framework guidelines.
  3. Strict No-Refusal Policy: NEVER state "I don't have information about this scheme" or "I can only answer about Scheme X and Y". If exact state-specific details are unavailable, explain general national guidelines and direct the farmer to official government portals (.gov.in / .nic.in).

==================================================
2. OBJECTION HANDLING
==================================================
Farmers may express doubt, frustration, or skepticism. Handle all objections professionally, empathetically, and accurately:
- Objection: "Application process is too complicated / No time." -> Break down into 3 simple steps, highlight CSC / Meeseva centers, and offer portal links.
- Objection: "Applied before, didn't get money / Rejected." -> Empathize, explain common rejection reasons (Aadhaar mismatch, land errors), and provide status-checking steps.
- Objection: "Is this genuine or a scam?" -> Provide official .gov.in links. Clarify that government schemes never ask for processing fees, OTPs, or passwords.
- Objection: "Small/tenant farmer eligibility." -> Clarify landholding rules clearly and mention alternative tenant/landless schemes.

==================================================
3. RESPONSE STRUCTURE
==================================================
1. Scheme Name & Brief Overview
2. Eligibility Criteria (Eligible & Excluded)
3. Documents Required
4. How to Apply (Step-by-Step)
5. Official Registration & Portal Links (e.g., https://pmkisan.gov.in/)

==================================================
4. PRIVACY & SENSITIVE DATA REDACTION (STRICT DIRECTIVE)
==================================================
- Absolute Zero-Disclosure: Never output, echo, or reproduce individual government identification digits for Aadhaar, South Korean RRN, or Japanese MyNumber under any circumstances.
- Redaction in Drafts/Forms: Use generic placeholders (e.g., [Aadhaar Redacted]).
- Conceptual Mentions Permitted: Explaining Aadhaar requirements conceptually (e.g., "Aadhaar card is required and must be linked to your bank account") is permitted.
"""

class FarmerRAGSystem:
    def __init__(self, json_file="farmer_schemes_master.json", index_folder="faiss_index"):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.vector_db = None
        self.index_folder = index_folder
        self._initialize_vector_store(json_file)

    def _initialize_vector_store(self, json_file):
        # 1. Check if FAISS local index already exists on disk
        if os.path.exists(self.index_folder):
            try:
                # Load persistent FAISS index from disk
                self.vector_db = FAISS.load_local(
                    self.index_folder, 
                    self.embeddings,
                    allow_dangerous_deserialization=True  # Required by LangChain for local pkl file loading
                )
                print(f"Successfully loaded existing FAISS index from {self.index_folder}")
                return
            except Exception as e:
                print(f"Error loading index: {e}. Rebuilding...")

        # 2. Build index from JSON if persistent store is missing
        if not os.path.exists(json_file):
            print(f"Warning: {json_file} not found. Operating in full dynamic fallback mode.")
            return

        with open(json_file, "r", encoding="utf-8") as f:
            schemes = json.load(f)

        docs = []
        for s in schemes:
            content = f"""
            Scheme Name: {s['scheme_name']}
            Portal URL: {s['portal_url']}
            Overview: {s['overview']}
            Eligibility: {json.dumps(s['eligibility_criteria'])}
            Documents: {', '.join(s['documents_required'])}
            How to Apply: {s['how_to_apply']}
            """
            docs.append(Document(page_content=content, metadata={"source": s['portal_url'], "name": s['scheme_name']}))

        if docs:
            # Create FAISS vector store in memory and save to disk
            self.vector_db = FAISS.from_documents(docs, self.embeddings)
            self.vector_db.save_local(self.index_folder)
            print(f"Created and saved new FAISS index to {self.index_folder}")

    def query(self, user_question: str) -> str:
        context_str = ""
        
        # 1. Primary Check: FAISS Local Vector Search
        if self.vector_db:
            # Perform L2 distance similarity search with distance scores
            results = self.vector_db.similarity_search_with_score(user_question, k=2)
            
            # Distance threshold filtering (lower score = closer match in FAISS L2 space)
            relevant_docs = [doc.page_content for doc, score in results if score < 0.8]
            if relevant_docs:
                context_str = "\n---\n".join(relevant_docs)

        # 2. Fallback Mechanism: Dynamic Retrieval trigger if no match
        if not context_str.strip():
            context_str = "LOCAL_DATABASE_MISSING: Scheme details not present in local store. Fall back to general structured knowledge to explain the official national scheme guidelines, eligibility, and portal URLs."

        # 3. Construct Prompt enforcing prompt rules
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "Retrieved Local Context:\n{context}\n\nFarmer Query: {query}")
        ])

        chain = prompt_template | self.llm
        response = chain.invoke({"context": context_str, "query": user_question})
        return response.content