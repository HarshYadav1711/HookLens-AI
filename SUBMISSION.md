# HookLens AI — Submission

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
