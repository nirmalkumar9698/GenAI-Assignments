# 🌾 Indian Farmer AI Assistant (RAG Application)

An intelligent Retrieval-Augmented Generation (RAG) assistant built using **Streamlit**, **LangChain**, **FAISS**, and **OpenAI**. The app provides Indian farmers and citizens with fast, accurate answers about central and state agricultural schemes, eligibility, required documentation, and application steps.

---

## 📌 Features

* **Real-time Scheme Information:** Detailed guidelines for schemes such as PM-KISAN, PMFBY, KCC, and SMSP.
* **Semantic Context Search:** Powered by FAISS vector embeddings to match user queries with relevant government scheme documents.
* **Interactive UI:** Built with Streamlit, featuring high-contrast custom styling and chat history persistence.
* **Automated Data Pipeline:** Includes Playwright web scrapers to gather and format scheme details directly from official government portals (e.g., *myScheme*).

---

## 🛠️ Architecture Overview

1. **Scraper (`scrape_all_schemes.py`):** Collects scheme metadata, structures structured JSON output, and extracts eligibility criteria and application workflows.
2. **Vector Indexing (`rag_engine.py`):** Loads scheme JSON data, chunks text, creates OpenAI embeddings, and stores vector representations in FAISS.
3. **Retrieval & QA Chain:** Retrieves top-matching scheme contexts for user prompts and synthesizes accurate answers without hallucination.
4. **Streamlit Interface (`app.py`):** Renders the conversational chat interface and preserves user chat context.

---

## 🚀 Setup & Local Execution

### 1. Prerequisites
* Python 3.10 or higher
* OpenAI API Key

### 2. Installation

Clone the repository and enter the project directory:
```bash
git clone [https://github.com/nirmalkumar9698/GenAI-Assignments.git](https://github.com/nirmalkumar9698/GenAI-Assignments.git)
cd GenAI-Assignments/Week2-RAG-Buildthon