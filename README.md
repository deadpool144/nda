# LexForge Contract Creator Platform

LexForge is an enterprise-grade AI-powered legal contract generation platform. It allows users to intuitively configure robust legal agreements (like NDAs) via a step-by-step form wizard, generate them deterministically through a rule-based engine, and seamlessly enhance the generated contracts using an advanced AI rewriting module backed by RAG (Retrieval-Augmented Generation).

## Features
- **Rule-Based Generation**: Deterministic rendering of complex legal structures.
- **AI Enhancement Mode**: Leverages Gemini 3.1 Flash Lite to smartly rewrite, expand, and enforce clauses based on custom user prompts while retaining factual constants.
- **Comparison View**: A side-by-side split view comparing the original Rule-Based generation with the AI-Reformed contract.
- **Live Risk Auditing**: An AI auditor tool that scans generated contracts for logical loopholes or highly risky terms.
- **DOCX Export**: Clean, properly formatted Microsoft Word export functionality for both Rule-Based and AI-Reformed contracts.
- **Vector Database Precedents**: Uses FAISS vector search to feed enterprise precedents into the LLM during drafting.

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd new_legal_ai
   ```

2. **Set up a Virtual Environment (Recommended)**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Install all required Python packages using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Configuration (`.env`)

Before running the application, you must set up your environment variables. 
Create a file named `.env` in the root of the project directory (`new_legal_ai/.env`) and add the following keys:

```ini
# Google Gemini API Key for AI enhancements and Embeddings
GEMINI_API_KEY=your_gemini_api_key_here

# The LLM model to use for Generation (e.g., gemini-3.1-flash-lite or gemini-2.5-flash)
LLM_MODEL=gemini-3.1-flash-lite

# The Embedding model to use for RAG (Retrieval-Augmented Generation)
EMBEDDING_MODEL=models/gemini-embedding-001
```

> **Note**: You can get your `GEMINI_API_KEY` from the [Google AI Studio](https://aistudio.google.com/).

## Initializing the Vector Database

Before running the app, you need to create the FAISS vector database from the sample legal precedents. Run the following script:

```bash
python -m backend.ai.rag.create_vector_db
```
This will read documents from the knowledge base and build the local `faiss_index`.

## Running the Application

Start the FastAPI application using Uvicorn from the root directory:

```bash
python -m uvicorn backend.main:app --reload
```

The application will start locally. Open your browser and navigate to:
**http://127.0.0.1:8000**

## Usage
1. Follow the on-screen steps to configure your legal agreement.
2. Advance to the final step to view the generated Rule-Based contract.
3. Click on the **AI Enhancement** button, enter a prompt (e.g., "Make the governing law clause heavily favorable to the disclosing party"), and click **Enhance with AI**.
4. Use the side-by-side view to compare your documents, run the AI Risk Auditor, and download the final version in DOCX format.
