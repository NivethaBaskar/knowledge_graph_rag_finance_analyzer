from fastapi import FastAPI
from rag_engine import rag_pipeline

app = FastAPI()

@app.get("/ask")
def ask(question: str):
    answer = rag_pipeline(question)
    return {"answer": answer}