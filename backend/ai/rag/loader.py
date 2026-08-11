import os
from langchain_community.document_loaders import Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(directory_path: str):
    docs = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".docx"):
                try:
                    loader = Docx2txtLoader(file_path)
                    doc = loader.load()[0]
                    # Tag with type for type-aware retrieval
                    doc.metadata["contract_type"] = determine_contract_type(file)
                    docs.append(doc)
                except Exception as e:
                    print(f"Error loading {file}: {e}")
            elif file.endswith(".txt"):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    doc = loader.load()[0]
                    doc.metadata["contract_type"] = determine_contract_type(file)
                    docs.append(doc)
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    return docs

def determine_contract_type(filename: str):
    name = filename.lower()
    if "nda" in name or "non-disclosure" in name:
        return "NDA"
    elif "employment" in name:
        return "Employment"
    elif "service" in name:
        return "Service"
    return "General"

def chunk_documents(documents, chunk_size=1200, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_documents(documents)
