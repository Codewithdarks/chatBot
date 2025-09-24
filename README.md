# ChatBot RAG System (Flask + Pinecone + Anthropic Claude)

This repository contains a simple Retrieval-Augmented Generation (RAG) pipeline:

- Ingestion (backend/ingest_api.py): fetches content from an API, chunks it, embeds with HuggingFace, and stores vectors in Pinecone.
- Backend API (backend/app.py): serves a /chat endpoint that retrieves relevant chunks from Pinecone and generates an answer using Anthropic Claude via LangChain.
- Pinecone setup (backend/setup_pinecone.py): one-time helper to create the Pinecone index with correct dimensions.
- Frontend (frontend/demo.html): minimal page you can expand to test the /chat endpoint.

## Requirements

- Python 3.10+
- Pinecone account and API key
- Anthropic API key

## Quick Start (for GitHub users)

1. Clone this repo:
   git clone https://github.com/your-org/ChatBot.git
   cd ChatBot
2. Create a virtual environment and install dependencies (Windows PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
3. Create your environment file based on the example:
   copy backend\.env.example backend\.env
   # then edit backend\.env and fill in your keys
4. Create the Pinecone index (one-time):
   python backend/setup_pinecone.py
5. Ingest data (choose one):
   - Static sample data: python backend/ingest_static.py
   - From your API: python backend/ingest_api.py
6. Run the backend server:
   python backend/app.py
7. Test the API:
   curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"query": "What is this project?"}'
8. Optional: open frontend/demo.html in your browser and try a query.

## Installation (detailed)

1. Clone the repository and navigate into it.
2. Create a virtual environment and install dependencies:

   - Windows (PowerShell):
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     pip install -r requirements.txt

3. Create a .env file in backend/ with the following variables (or copy from backend/.env.example):

   ANTHROPIC_API_KEY=your_anthropic_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   # Region for Pinecone Serverless (e.g., us-east-1, eu-west-1). Must match where you create the index.
   PINECONE_ENVIRONMENT=us-east-1

4. Configure your API source for ingestion:
   - Edit backend/ingest_api.py and set API_ENDPOINT to your content API that returns a JSON list where each item contains fields like "title" and "content".

## Pinecone Index Setup

Run the one-time setup to create the index (or confirm it exists):

   python backend/setup_pinecone.py

- The index name is rag-index and uses 768 dimensions to match the sentence-transformers/all-mpnet-base-v2 embeddings.
- If you need a different model, update both the embedding model in code and the index dimension to match.

## Ingest Content

After the index is created, you have two options to add data into Pinecone:

1) Static sample data (recommended for quick Postman testing):

   python backend/ingest_static.py

- This will insert a handful of predefined documents so you can query immediately.

2) From your own API:

   python backend/ingest_api.py

- This will fetch documents from API_ENDPOINT, split into chunks, embed, and upsert into the rag-index index.

## Run the Backend Server

Start the Flask server:

   python backend/app.py

- The API will run at http://localhost:5000
- Endpoint: POST /chat with JSON body {"query": "your question"}

Example using curl (PowerShell; escape quotes accordingly):

   curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"query": "What is X?"}'

## Test via Frontend

Open frontend/demo.html in a browser (or serve it via a static server). You can edit it to call http://localhost:5000/chat with fetch and display responses.

## Common Pitfalls and Notes

- Ensure .env is present in backend/ before running scripts so load_dotenv() can pick up keys.
- The Pinecone SDK here uses ServerlessSpec with cloud=aws and region=PINECONE_ENVIRONMENT. Example regions: us-east-1, eu-west-1, ap-southeast-1.
- The langchain_pinecone integration expects the pinecone index to exist; run setup_pinecone.py first.
- The embedding model sentence-transformers/all-mpnet-base-v2 yields 768-dimensional vectors, matching the configured index dimension.
- ChatAnthropic in app.py uses ANTHROPIC_API_KEY; ensure this key has access to the specified Claude model (e.g., claude-3-5-sonnet-latest).

## Security and .gitignore

- Secrets: Do NOT commit real API keys. Use backend/.env (ignored by .gitignore). Share backend/.env.example instead.
- .gitignore: We include patterns for Python caches, virtualenvs (.venv/), IDE folders (.idea/, .vscode/), OS files, logs, node_modules, and environment files (.env).
- If you accidentally committed secrets in the past:
  1) Immediately rotate the keys in Anthropic and Pinecone dashboards.
  2) Remove the file from git history: git rm --cached backend/.env; commit; then consider using git filter-repo or the GitHub instructions to remove secrets from history.
  3) Force-push only if you fully understand the implications; coordinate with collaborators.

## Fix Log (what was checked and adjusted)

- Added basic frontend demo to call POST /chat (frontend/demo.html). ✓
- app.py: switched LLM to Anthropic ChatAnthropic with ANTHROPIC_API_KEY; kept llm.invoke compatibility and normalized response text extraction. ✓
- setup_pinecone.py: added validation for PINECONE_API_KEY and PINECONE_ENVIRONMENT before creating index; fixed a typo in comment; clarified that PINECONE_ENVIRONMENT is the serverless region. ✓
- ingest_api.py: made API endpoint configurable via INGEST_API_ENDPOINT in .env; added warnings when placeholder is used; added guards and clearer logs when no data/documents; ensured PINECONE_API_KEY presence before proceeding. ✓
- Verified consistent index name: rag-index across setup_pinecone.py, ingest_api.py, app.py. ✓
- Confirmed embedding model consistency (all-mpnet-base-v2, 768 dims) and index dimension in setup_pinecone.py. ✓
- Ensured environment variables loaded via python-dotenv in all backend scripts. ✓
- Note: ingest_api.py's default endpoint is a placeholder (https://api.example.com/v1/articles); set INGEST_API_ENDPOINT to your real source. ✓

If you encounter module import issues:
- Ensure the versions in requirements.txt are installed (pip install -r requirements.txt).
- If langchain APIs change, pin versions or update imports accordingly.
- Ensure ANTHROPIC_API_KEY is set in backend/.env and that your account has access to the selected Claude model.

## Extending

- Add authentication and rate-limiting to the Flask API.
- Enhance frontend to provide chat UI and maintain conversation context.
- Add ingestion from files or sitemaps in addition to API sources.
