import streamlit as st
import requests
import pandas as pd
from db import driver

# --- CONFIG ---
st.set_page_config(page_title="Personal Finance AI", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d6efd;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_stats():
    """Fetch quick metrics from Neo4j."""
    try:
        with driver.session() as session:
            # Count transactions
            tx_count = session.run("MATCH (n:Expense) RETURN count(n) as c1, (MATCH (m:Income) RETURN count(m)) as c2").single()
            total_tx = (tx_count[0] if tx_count else 0) + (tx_count[1] if tx_count and len(tx_count)>1 else 0)
            
            # Count Amazon spend specifically for the demo
            amazon = session.run("MATCH (e:Expense) WHERE toUpper(e.narration) CONTAINS 'AMAZON' RETURN count(e) as c").single()
            amazon_count = amazon['c'] if amazon else 0
            
            return total_tx, amazon_count
    except Exception as e:
        return 0, 0

def ask_ai(question):
    """Call the FastAPI backend."""
    try:
        response = requests.get(f"http://127.0.0.1:8000/ask?question={question}")
        if response.status_code == 200:
            return response.json().get("answer", "No answer received.")
        else:
            return f"Error: API returned {response.status_code}"
    except Exception as e:
        return f"Could not connect to backend: {str(e)}"

# --- UI LAYOUT ---
st.markdown('<div class="main-header">💰 Personal Finance Knowledge Graph</div>', unsafe_allow_html=True)

# Sidebar (Left)
with st.sidebar:
    st.header("📊 Overview")
    tx_count, amz_count = get_stats()
    
    st.markdown("### Metrics")
    st.metric("Total Transactions", tx_count)
    st.metric("Amazon Orders", amz_count)
    
    st.divider()
    st.markdown("### 🛠 Tools")
    if st.button("🔄 Sync Statement (ingestion)"):
        with st.spinner("Processing acc_statement.xls..."):
            try:
                from ingestor import load_data
                load_data()
                st.success("Database Refreshed!")
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}")

# Main Area (Two Columns)
col_main, col_right = st.columns([3, 1], gap="large")

with col_main:
    # Chat/Query Interface
    st.markdown("### 💬 Ask Nivetha's Finance Assistant")
    user_query = st.chat_input("Ex: What was my total expense in the month of April?")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.status("🚀 Processing Knowledge RAG...", expanded=True) as status:
                st.write("🔍 Analyzing query intent...")
                # Simulate small delays or just proceed to give the 'step' feel
                st.write("🕸️ Querying Neo4j Knowledge Graph...")
                answer = ask_ai(user_query)
                st.write("⚖️ Synthesizing results with LLM...")
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
            
            st.markdown(answer)

with col_right:
    st.markdown("### 💡 Suggestions")
    st.info("Click to see example queries:")
    
    if st.button("Total spent with John"):
        st.info("Ask: How much did I spend with John in total?")
        
    if st.button("List March transactions"):
        st.info("Ask: List all transactions for March")
        
    if st.button("Highest spending category"):
        st.info("Ask: To whom i transferred most?")
        
    if st.button("Amazon order count"):
        st.info("Ask: How many Amazon transactions did I have?")


