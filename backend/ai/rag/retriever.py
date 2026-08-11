from backend.ai.rag.vector_store import load_vector_store

class ContractRetriever:
    def __init__(self):
        self.vectorstore = load_vector_store()
        
    def retrieve(self, query: str, contract_type: str, k: int = 8):
        if not self.vectorstore:
            return []
            
        # Optional: Perform contract-type aware filtering if FAISS supports metadata filtering
        # Langchain FAISS supports filtering via metadata
        
        # Determine base type for filter
        type_filter = "General"
        if "nda" in contract_type.lower():
            type_filter = "NDA"
        elif "employment" in contract_type.lower():
            type_filter = "Employment"
        elif "service" in contract_type.lower():
            type_filter = "Service"
            
        filter_dict = {"contract_type": type_filter}
        
        try:
            # Try with filter
            docs = self.vectorstore.similarity_search(query, k=k, filter=filter_dict)
            if not docs:
                # Fallback if no specific docs exist
                docs = self.vectorstore.similarity_search(query, k=k)
            return docs
        except Exception:
            # Fallback for FAISS without filter support
            return self.vectorstore.similarity_search(query, k=k)
