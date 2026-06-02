# Architecture Decision Records — HookLens AI

This document records why the prototype is built the way it is. Each entry states the problem, the choice made in this repo, and the tradeoffs accepted. It reflects **current implementation**, not a production roadmap.

---

## ADR-001: FastAPI for the HTTP API

**Status:** Accepted

**Context.** The backend must expose ingest, index, health, and streaming chat endpoints to a Next.js client. Ingestion mixes async orchestration with blocking work (yt-dlp, Whisper, embedding encode) delegated to threads.

**Decision.** Use FastAPI with Pydantic request/response models and native `async` route handlers where I/O-bound (Ollama HTTP, graph streaming).

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Automatic OpenAPI schema and validation align with typed `schemas/` | Heavier than a minimal framework for a handful of routes |
| `async` fits SSE (`EventSourceResponse`) and httpx to Ollama | Blocking CPU work still needs `asyncio.to_thread` or sync call sites—FastAPI does not remove GIL-bound embedding cost |
| Familiar Python stack for ML-adjacent dependencies | No built-in job queue; long ingest runs hold a request until complete |

**Alternatives considered.** Flask (fewer async ergonomics for SSE); Django (more structure than needed for a demo API).

---

## ADR-002: LangGraph for the comparison pipeline

**Status:** Accepted

**Context.** Chat must run a fixed sequence: retrieve transcript chunks → build comparison facts → assemble numbered citations → stream generation → update thread memory. Early exits are required when the session is missing or not indexed.

**Decision.** Model the flow as a compiled `StateGraph` (`retrieve` → `reasoning` → `citation_assembly` → `generate` → `memory_update`) with SQLite checkpointing for per-thread history.

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Explicit nodes match the product’s retrieve-before-generate contract | LangGraph + checkpoint dependencies add operational surface (SQLite file under `data/checkpoints.db`) |
| `get_stream_writer()` emits `citations`, `token`, `done`, `error` without ad-hoc generators in routes | Graph compile/setup at app startup; harder to reason about than a single function for very small teams |
| Conditional routing after retrieve (e.g. skip reasoning when retrieval fails) | Overkill if the pipeline never grows beyond five steps—acceptable here because streaming and memory are first-class |

**Alternatives considered.** Plain async function calling retrieve + Ollama directly (less visibility into stages; harder to extend with checkpointed follow-ups).

**Not claimed.** LangGraph does not improve retrieval quality by itself; it only structures when retrieval, citation assembly, and generation run.

---

## ADR-003: Qdrant for vector storage

**Status:** Accepted

**Context.** Each analyze run produces many transcript chunks that must be searched by semantic similarity at question time. The prototype runs locally alongside Docker Compose.

**Decision.** Store chunk embeddings in a single Qdrant collection (`hooklens_chunks`), filtered by `session_id` at query time. Vectors are produced in-process with Sentence Transformers (`all-MiniLM-L6-v2`); metadata (platform, timestamps, text) lives in the payload.

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Purpose-built ANN search with payload filters for session isolation | Another service to run (`docker compose up -d`); `/api/health` does not deeply verify Qdrant |
| Simple local setup via official image | Single collection, no tenant sharding—fine for demos, not for multi-tenant production |
| Decouples “index once” from “retrieve many times” per session | Re-index and delete logic must be maintained when transcripts change (fingerprint-based skip helps) |

**Alternatives considered.** In-memory numpy cosine search (loses persistence across restarts); pgvector (more ops for a comparison demo); managed cloud vector DB (cost and setup friction for reviewers).

---

## ADR-004: Ollama for text generation

**Status:** Accepted

**Context.** Answers must be generated from retrieved evidence with streaming tokens in the UI. The assignment target environment is local development without a mandatory cloud LLM key.

**Decision.** Call Ollama’s HTTP chat API (`OLLAMA_BASE_URL`, default `llama3.2`) from `generate_node`; health endpoint reports whether Ollama responds.

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Zero API key friction for local evaluation | Quality and speed depend on local hardware and model choice |
| Streaming matches Ollama’s line-delimited JSON stream | No centralized quota, logging, or content policy layer |
| Swappable via env vars without code changes to the graph shape | Single-model default; no routing between “fast” and “deep” models in this repo |

**Alternatives considered.** Hosted OpenAI/Azure (better ops, requires secrets and spend controls). **Not in scope:** fine-tuning, tool calling, or vision over video frames—only text prompts built from transcripts and metadata.

---

## ADR-005: Session-scoped indexing

**Status:** Accepted

**Context.** Each UI “Analyze” compares exactly one YouTube URL and one Instagram Reel. Reviewers run multiple demos; data must not leak between runs. The prototype has no authentication.

**Decision.** Assign a UUID `session_id` per ingest. Persist normalized videos as JSON under `data/sessions/`. Index chunks into Qdrant with `session_id` in the payload; retrieval always filters on that id. Skip re-embedding when the transcript fingerprint is unchanged.

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Strong isolation between demo runs without multi-tenant auth | No shared workspace or cross-session search |
| Fingerprint skip avoids redundant embedding on re-Analyze | Orphan vectors if sessions are deleted on disk but not purged from Qdrant (no GC job in prototype) |
| Matches UI mental model: one pair → one chat thread context | Session files on local disk are not encrypted or replicated |

**Alternatives considered.** Global index with user-provided labels (risk of cross-talk); per-video indices without pairing (harder to enforce A vs B comparison in prompts).

---

## ADR-006: SSE instead of WebSockets for chat streaming

**Status:** Accepted

**Context.** The client sends a question via `POST` and receives streamed citations, tokens, and completion over a single HTTP response. Traffic is server → client only after the POST body is sent.

**Decision.** Use Server-Sent Events (`EventSourceResponse` + `fetch` readable stream on the frontend) with event types `citations`, `token`, `done`, `error`.

**Tradeoffs.**

| Benefit | Cost |
|---------|------|
| Works with standard POST + JSON body (session id, message, thread_id) | No bidirectional channel—each turn is a new POST |
| Easier to debug in browser devtools and curl than WS frames | Some proxies buffer SSE unless configured; less of an issue on localhost |
| Aligns with one-way LLM token stream | Cannot push server events without a client request (acceptable for Q&A, not for live notifications) |

**Alternatives considered.** WebSockets (extra connection lifecycle and auth complexity for no client-to-server stream requirement); long polling (higher latency and messier citation ordering).

---

## Cross-cutting constraint

These decisions optimize for **local reviewer setup** (Docker Qdrant + Ollama + uvicorn + Next.js), **evidence-grounded answers** (retrieve and cite before generate), and **honest scope** (transcript text and ingested metadata only). Production deployment would revisit auth, managed Qdrant/LLM, ingest job queues, and observability—see README **Known limitations**.
