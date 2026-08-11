import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.ai.rag.loader import load_documents, chunk_documents
from backend.ai.rag.vector_store import save_vector_store

def build_index():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    docs_dir = os.path.join(base_dir, "docs")
    
    print(f"Loading documents from {docs_dir}...")
    docs = load_documents(docs_dir)
    print(f"Loaded {len(docs)} documents.")
    
    if not docs:
        print("No documents found to index.")
        return
        
    print("Chunking documents...")
    chunks = chunk_documents(docs, chunk_size=1200, chunk_overlap=150)
    print(f"Created {len(chunks)} chunks.")
    
    print("Generating embeddings and saving FAISS index...")
    save_vector_store(chunks)
    print("Done!")

if __name__ == "__main__":
    build_index()
