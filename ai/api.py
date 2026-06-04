from fastapi import FastAPI
from pydantic import BaseModel
from ai.chatbot import answer_question
import uvicorn

app = FastAPI(title="JobLens AI API")

class Question(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "JobLens AI is running!"}

@app.post("/ask")
def ask(q: Question):
    answer = answer_question(q.question)
    return {"question": q.question, "answer": answer}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("ai.api:app", host="0.0.0.0", port=8000, reload=True)