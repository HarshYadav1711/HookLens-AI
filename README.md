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

- **Ingestion** — `POST /api/ingest` → `session_id` + normalized metadata/transcripts (YouTube = **A**, Instagram = **B**).
- **Indexing** — `POST /api/sessions/{session_id}/index` chunks, embeds (Sentence Transformers), stores in Qdrant. Re-index is skipped when the transcript fingerprint is unchanged.
- **Retrieval** — `POST /api/sessions/{session_id}/retrieve` with `{ "query", "video_label"?, "video_id"? }` (query-only embedding at search time).
- **Reasoning (LangGraph)** — `POST /api/sessions/{session_id}/chat/stream` (SSE) or `/chat` with `{ "message", "thread_id"? }`. Graph nodes: retrieve → reasoning → citation assembly → generate → memory update. Checkpointed threads for follow-ups.
- **Frontend** — not implemented yet.

Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
