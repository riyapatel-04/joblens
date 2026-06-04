import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    return vectorstore

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def answer_question(question: str) -> str:
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 15})
    
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0
    )
    
    prompt = ChatPromptTemplate.from_template("""
You are JobLens AI — an expert job market analyst.
Use ONLY the job postings data below to answer the question.
Be specific, data-driven, and helpful.
Extract skills, salaries, companies, and locations from the context.
If the data doesn't contain enough info, say so honestly.

Job postings context:
{context}

Question: {question}

Provide a clear, structured answer:
""")
    
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(question)

if __name__ == "__main__":
    print("🤖 JobLens AI Chatbot")
    print("=" * 40)
    
    questions = [
        "What skills are most in demand for data engineers?",
        "Which companies are hiring data analysts in Boston?",
        "What is the average salary for analytics engineers?"
    ]
    
    for q in questions:
        print(f"\n❓ {q}")
        print(answer_question(q))
        print("-" * 40)