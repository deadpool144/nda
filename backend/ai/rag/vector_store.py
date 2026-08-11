import os
from langchain_community.vectorstores import FAISS
from backend.ai.models.provider import get_embedding_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "ai", "rag", "faiss_index")

import time

def save_vector_store(docs):
    embeddings = get_embedding_model()
    
    batch_size = 50
    vectorstore = None
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        print(f"Embedding batch {i//batch_size + 1}/{(len(docs)//batch_size) + 1}...")
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if vectorstore is None:
                    vectorstore = FAISS.from_documents(batch, embeddings)
                else:
                    vectorstore.add_documents(batch)
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit. Sleeping for 15s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(15)
                else:
                    raise e
                    
        time.sleep(4)
        
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")
    return vectorstore
def load_vector_store():
    if not os.path.exists(FAISS_INDEX_PATH):
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
