from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------------
# 🧠 EXACT SCHEMA DEFINITION
# -------------------------------
def get_manual_schema():
    return """
    Nodes:
    - Person {{name: 'Nivetha'}}
    - Expense {{amount: FLOAT, date: STRING, narration: STRING}}
    - Income {{amount: FLOAT, date: STRING, narration: STRING}}
    
    Relationships:
    - (:Person)-[:SPENT]->(:Expense)
    - (:Person)-[:RECEIVED]->(:Income)
    
    Path Rule:
    - Every transaction (Expense or Income) is connected directly to the Person (Nivetha). 
    - Always use exactly one relationship hop: (p:Person {{name: "Nivetha"}})-[:SPENT|RECEIVED]->(n)
    """

CYPHER_GENERATION_TEMPLATE = """Task: Generate a Cypher statement to query a Neo4j graph database.
Use ONLY the properties and relationships specified in the schema below.

Schema:
{schema}

Instructions:
1. Use exactly one relationship hop from the user.
2. For ANY transaction query (list, total, search), use: MATCH (p:Person {{name: "Nivetha"}})-[:SPENT|RECEIVED]->(n)
3. For spending/expenses specifically: use MATCH (p:Person {{name: "Nivetha"}})-[:SPENT]->(n:Expense)
4. For income specifically: use MATCH (p:Person {{name: "Nivetha"}})-[:RECEIVED]->(n:Income)
5. To filter by month: use 'n.date CONTAINS "/03/"' for March, '/04/' for April, etc.
5. For name/vendor searches: use 'toUpper(n.narration) CONTAINS toUpper("name")'.
6. End ONLY with 'RETURN n' or 'RETURN count(n)'.
7. Do not use any labels or properties not in the schema.

Question: {question}
Cypher Statement:"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], 
    template=CYPHER_GENERATION_TEMPLATE
)

QA_TEMPLATE = """Task: Answer the user's question based on the provided results.
Context: {context}
Question: {question}

Format for listing transactions:
* **[Date]** | **[Amount] INR** | **[Narration]**

Answer:"""

QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=QA_TEMPLATE)

# -------------------------------
# 🏗️ SYSTEM INITIALIZATION
# -------------------------------
llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="knowledge_graph_demo_2024",
    refresh_schema=False
)

manual_schema = get_manual_schema()

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
    cypher_prompt=CYPHER_PROMPT.partial(schema=manual_schema),
    qa_prompt=QA_PROMPT
)

# -------------------------------
# 🎯 PIPELINE
# -------------------------------
def rag_pipeline(question):
    print(f"\n[QUERY] {question}")

    query_lower = question.lower()
    financial_keywords = ["spend", "expense", "transaction", "amazon", "income", "balance", "total", "received", "transfered", "list", "show", "month", "under", "above"]
    
    if any(word in query_lower for word in financial_keywords):
        try:
            res = chain.invoke({"query": question})
            return res.get("result", "") if isinstance(res, dict) else res
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return llm.invoke(question).content