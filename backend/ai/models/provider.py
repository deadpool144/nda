import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"))

def get_generation_llm():
    model_name = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2, # Low temp for deterministic legal drafting
        max_output_tokens=8192
    )

def get_embedding_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("EMBEDDING_MODEL", "models/embedding-001")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")
        
    return GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=api_key
    )
