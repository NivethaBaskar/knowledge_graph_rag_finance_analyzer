# 💰 Personal Finance Knowledge Graph Assistant

An AI-powered financial analyzer that transforms your semi-structured bank statements into a **Neo4j Knowledge Graph** and allows you to query it using natural language through a **RAG (Retrieval-Augmented Generation)** pipeline.

## 🚀 Key Features
*   **Automated Ingestion**: Syncs `.xls` bank statements directly into Neo4j nodes (Income, Expense, Category).
*   **Knowledge Graph RAG**: Uses an adaptive AI engine to translate natural language into Cypher queries.
*   **Deep Financial Analytics**:
    *   Filter by **Person** (e.g., "Nivetha").
    *   Search by **Name/Vendor** (e.g., "Athish", "Amazon").
    *   Analyze by **Amount** (e.g., "Under 500").
    *   Time-based queries (Month/Date wise).
*   **Modern Workspace**: A bright, premium Streamlit dashboard with real-time metrics and query suggestions.
*   **Transparent Processing**: View the internal RAG steps (Analysis -> Retrieval -> Synthesis) live in the UI.

## 🏗️ Technical Stack
*   **Database**: Neo4j Graph Database
*   **Orchestration**: LangChain + GraphCypherQAChain
*   **Intelligence**: OpenAI GPT models
*   **Backend**: FastAPI
*   **Frontend**: Streamlit
*   **Data Processing**: Pandas + xlrd (for XLS parsing)

## 📁 Project Structure
```text
├── backend/
│   ├── app.py           # FastAPI Main Entry
│   ├── rag_engine.py    # AI & Knowledge Graph Logic
│   ├── ingestor.py      # Bank Statement Parser
│   ├── db.py            # Neo4j Driver Setup
│   └── frontend.py      # Streamlit UI
├── data/
│   └── acc_statement.xls # Your Bank Statement (Source)
└── .gitignore           # Safety rules for .env and venv
```

## 🛠️ Setup & Installation

### 1. Prerequisites
*   Install **Neo4j Desktop** or run a Neo4j instance.
*   Configure a database with user: `neo4j` and password: `knowledge_graph_demo_2024`.

### 2. Environment Variables
Create a `.env` file in the root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Running the Backend (FastAPI)
```bash
cd backend
pip install fastapi uvicorn langchain langchain-neo4j langchain-openai pandas xlrd python-dotenv
uvicorn app:app --reload
```

### 4. Running the Frontend (Streamlit)
```bash
# In a new terminal
cd backend
streamlit run frontend.py
```

## 📊 Data Ingestion
1. Place your bank statement file in `data/acc_statement.xls`.
2. Open the Streamlit Dashboard.
3. Click the **🔄 Sync Statement** button in the sidebar to load your data into the graph.

## 💡 Example Queries
*   "List all transactions for March"
*   "Show me transactions under 500 INR"
*   "How much did I receive from Athish?"
*   "What was my total spending on Amazon?"

---
*Created by Nivetha Baskar*
