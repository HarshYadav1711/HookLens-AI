# HookLens AI — Submission

## Quick project summary

HookLens AI is a dual-video comparison tool: **YouTube = Video A**, **Instagram Reel = Video B**. It ingests public URLs, builds session-scoped transcript indexes in Qdrant, and answers comparison questions with **streaming text plus numbered citations** (platform, time range, excerpt). Generation uses retrieved transcript evidence only—not platform analytics APIs.

Local stack: Next.js UI · FastAPI · LangGraph · Sentence Transformers · Qdrant · Ollama. See [README.md](./README.md) for setup and [ADR.md](./ADR.md) for design rationale.

---

## Key capabilities

| Capability | What to look for |
|------------|------------------|
| **Dual ingest** | Metadata and transcripts for both URLs after **Analyze** |
| **Vector index** | Progress reaches **Ready** with chunks indexed (Qdrant) |
| **Grounded chat** | SSE-streamed answers citing `[1]`, `[2]`, … |
| **Sources panel** | Citation cards under each reply match transcript excerpts |
| **A vs B labeling** | Answers distinguish YouTube (A) and Instagram (B) |
| **Recovery UX** | Failures name what broke (API, Qdrant, Ollama, ingest) and a next step |

Out of scope for this build: auth, official Insights APIs, visual/frame analysis, production multi-tenant hosting.

---

## Suggested evaluation flow

1. **Setup (if running locally)** — `docker compose up -d`, `ollama serve`, backend `:8000`, frontend `:3000`; `GET /api/health` → `ollama: true`.
2. **Deployed URL or Loom** — Open submitted Project URL or watch Loom first for the happy path.
3. **Analyze** — Two public URLs → **Extract → Index → Ready** (allow 1–2 min on first run).
4. **Surface data** — Video cards, comparison summary, full transcripts.
5. **Chat** — Use **Suggested Questions** (e.g. first 5 seconds, hook comparison); confirm **Sources** align with transcript text.
6. **Spot-check grounding** — Pick one `[n]` citation and verify the excerpt at that timestamp in the transcript pane.

Optional: README **What To Test** and **Expected Evidence Behavior** for pass/fail detail.

---

## Demo checklist

Use when reviewing the Loom or a live session:

- [ ] Two public URLs pasted; **Analyze** completes through **Ready**
- [ ] Video A (YouTube) and Video B (Instagram) cards show metrics and transcripts
- [ ] At least one chat question answered with streaming text
- [ ] **Sources** list shows numbered citations with timestamps and excerpts
- [ ] Answer references Video A vs Video B where relevant
- [ ] Opening-hook question (first **5 seconds**) cites early transcript lines when speech exists
- [ ] **How answers are generated** in the chat panel matches retrieve → cite → generate behavior

---

Copy the block below into the submission form. Replace every `YOUR_*` placeholder before submitting.

---

**1. Project URL**

```
YOUR_DEPLOYED_APP_URL
```
---

**2. Project Description**

```
HookLens AI compares a YouTube video and an Instagram Reel side by side. Paste both URLs, run Analyze to extract metadata and transcripts, index transcript evidence in Qdrant, then ask natural-language questions in chat. Every answer streams in real time and includes numbered citations (platform, timestamp range, and excerpt) tied to retrieved transcript chunks. Built with Next.js, FastAPI, LangGraph, Sentence Transformers, Qdrant, and Ollama.
```

---

**3. Loom URL**

```
YOUR_LOOM_VIDEO_URL
```

---

**4. Github repo**

```
https://github.com/HarshYadav1711/HookLens-AI
```
---

## Pre-submit checklist

- [ ] `SUBMISSION.md` placeholders replaced
- [ ] README Loom checklist followed on a fresh Analyze run
- [ ] `backend/.env` and `frontend/.env.local` configured (not committed)
- [ ] Qdrant (`docker compose up -d`) and Ollama (`ollama pull llama3.2`) verified
- [ ] Loom shows: paste URLs → Analyze → summary/transcripts → chat with citations
