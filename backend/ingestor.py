import pandas as pd
import os
from db import driver

def get_category(narration):
    """Simple keyword-based categorization."""
    narration = str(narration).lower()
    if "amazon" in narration or "flipkart" in narration:
        return "Shopping"
    elif "upi" in narration:
        return "Transfer"
    elif "fuel" in narration or "hpcl" in narration or "bpcl" in narration:
        return "Transport"
    elif "swiggy" in narration or "zomato" in narration or "restaurant" in narration:
        return "Food"
    elif "salary" in narration or "credit" in narration:
        return "Income"
    else:
        return "Others"

def insert_transaction(tx, t):
    """Neo4j session write transaction function."""
    # Determine the node label and relationship based on withdrawal vs deposit
    if t["withdrawal"] > 0:
        label = "Expense"
        rel = "SPENT"
        amount = float(t["withdrawal"])
    else:
        label = "Income"
        rel = "RECEIVED"
        amount = float(t["deposit"])

    tx.run(f"""
        MERGE (p:Person {{name: "Nivetha"}})
        MERGE (c:Category {{name: $category}})

        CREATE (e:{label} {{
            date: $date,
            amount: $amount,
            currency: "INR",
            narration: $narration
        }})

        MERGE (p)-[:{rel}]->(e)
        MERGE (e)-[:BELONGS_TO]->(c)
    """,
    date=str(t["date"]),
    amount=amount,
    narration=str(t["narration"]),
    category=get_category(t["narration"])
    )

def load_data():
    # Resolve file path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    file_path = os.path.join(project_root, "data", "acc_statement.xls")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Reading bank statement from {file_path}...")
    
    # Read XLS, skipping the first 20 lines of header metadata
    df = pd.read_excel(file_path, skiprows=20)

    # Rename columns for easier access
    df = df.rename(columns={
        'Date': 'date',
        'Narration': 'narration',
        'Withdrawal Amt.': 'withdrawal',
        'Deposit Amt.': 'deposit'
    })

    # Filter out empty rows and the '********' decoration
    df = df[df['date'].astype(str).str.contains(r'\d{2}/\d{2}/\d{2}', na=False)]
    
    # Strip any potential literal quotes from the date string
    df['date'] = df['date'].astype(str).str.strip('"')
    
    # Convert amounts to numeric, handling NaN
    df['withdrawal'] = pd.to_numeric(df['withdrawal'], errors='coerce').fillna(0)
    df['deposit'] = pd.to_numeric(df['deposit'], errors='coerce').fillna(0)

    count = 0
    with driver.session() as session:
        for _, row in df.iterrows():
            session.execute_write(insert_transaction, row)
            count += 1
            
    print(f"Successfully loaded {count} transactions into Neo4j (Clean Start)!")

if __name__ == "__main__":
    load_data()
