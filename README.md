# HookLens AI

Compare two social videos (YouTube vs Instagram Reel) and explain, with evidence, why one performed better than the other.

## Architecture

```
hooklens-ai/
├── frontend/          # Next.js + TypeScript + Tailwind (UI)
└── backend/           # FastAPI (API, ingest, RAG)
        ├── ingestion/ # Video metadata & transcript extraction
        ├── retrieval/ # Vector search & citations
        ├── graph/     # LangGraph orchestration
        ├── models/    # Domain models
        ├── schemas/   # API contracts (Pydantic)
        ├── services/  # Embeddings, storage, LLM clients
        └── utils/     # Shared helpers
```

Planned data flow: **ingest two URLs → chunk & embed transcripts → retrieve evidence → stream cited answers**.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

App: [http://localhost:3000](http://localhost:3000)

## Status

Scaffold only — ingestion, retrieval, and chat are not implemented yet.
