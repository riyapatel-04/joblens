import json
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

load_dotenv()

def load_jobs_as_documents():
    with open("validated_jobs.json", "r") as f:
        jobs = json.load(f)
    
    documents = []
    for job in jobs:
        content = f"""
        Job Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Location: {job.get('location', '')}
        Role: {job.get('search_role', '')}
        Category: {job.get('category', '')}
        Salary Min: {job.get('salary_min', 'Not specified')}
        Salary Max: {job.get('salary_max', 'Not specified')}
        Description: {job.get('description', '')[:500]}
        """
        metadata = {
            "job_id": str(job.get("id", "")),
            "title": str(job.get("title", "")),
            "company": str(job.get("company", "")),
            "location": str(job.get("location", "")),
            "search_role": str(job.get("search_role", "")),
            "salary_min": str(job.get("salary_min", "")),
            "salary_max": str(job.get("salary_max", "")),
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    print(f"📄 Created {len(documents)} documents")
    return documents

def create_vector_store():
    print("🔄 Loading jobs...")
    documents = load_jobs_as_documents()
    
    print("🔄 Creating embeddings with free local model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print(f"✅ Vector store created with {len(documents)} job embeddings")
    print("✅ Saved to ./chroma_db")
    return vectorstore

if __name__ == "__main__":
    create_vector_store()