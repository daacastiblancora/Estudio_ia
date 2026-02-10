# Copiloto Core (RAG Backend)

Backend services for the Corporate Operational Copilot.

## Context
This system answers operational questions based on internal documents (PDF/DOCX) using RAG (Retrieval-Augmented Generation).

## Stack
- **Language**: Python 3.11+
- **API**: FastAPI
- **LLM**: Groq (Llama 3)
- **Vector DB**: Qdrant Cloud
- **Orchestration**: LangChain

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   Copy `.env.example` to `.env` and add your API keys.

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
Once running, visit `http://localhost:8000/docs` for the interactive API documentation.
