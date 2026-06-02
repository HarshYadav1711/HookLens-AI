/** Normalize FastAPI / fetch error payloads into a single user-facing string. */
export function formatApiErrorDetail(detail: unknown): string {
  if (detail == null) return "Request failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: string }).msg);
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }
  if (typeof detail === "object" && "message" in detail) {
    return String((detail as { message: string }).message);
  }
  return String(detail);
}

export function isNetworkError(err: unknown): boolean {
  return (
    err instanceof TypeError &&
    (err.message === "Failed to fetch" || err.message.includes("NetworkError"))
  );
}

export function formatRecoveryGuidance(
  whatFailed: string,
  likelyCause: string,
  nextStep: string,
): string {
  return `What failed: ${whatFailed}\n\nLikely cause: ${likelyCause}\n\nNext step: ${nextStep}`;
}

function apiUnreachableGuidance(): string {
  return formatRecoveryGuidance(
    "The browser could not reach the HookLens API.",
    "The FastAPI backend is not running, is on a different host/port, or NEXT_PUBLIC_API_URL in frontend/.env.local does not match where uvicorn is listening.",
    "From the repo root, start the backend (`cd backend` then `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`), confirm http://localhost:8000/api/health opens, and set NEXT_PUBLIC_API_URL to that origin (no trailing slash). Then retry.",
  );
}

function ollamaUnavailableGuidance(detail?: string): string {
  const suffix = detail ? ` Server detail: ${detail}` : "";
  return formatRecoveryGuidance(
    "Chat could not generate an answer (Ollama).",
    `The local LLM service is not running, is not reachable at OLLAMA_BASE_URL (default http://localhost:11434), or the configured model is not installed.${suffix}`,
    "In a terminal run `ollama serve`, pull the model (`ollama pull llama3.2`), verify with `ollama list`, confirm http://localhost:8000/api/health shows ollama: true, then send your question again.",
  );
}

function qdrantUnavailableGuidance(detail?: string): string {
  const suffix = detail ? ` Server detail: ${detail}` : "";
  return formatRecoveryGuidance(
    "Transcript indexing could not write vectors to Qdrant.",
    `The vector database is not running or is not reachable at QDRANT_URL (default http://localhost:6333).${suffix}`,
    "From the repo root run `docker compose up -d`, wait until Qdrant is healthy, confirm port 6333 is open, then click Analyze again (extraction may already have finished).",
  );
}

function matchesOllamaFailure(lower: string): boolean {
  return (
    lower.includes("ollama") ||
    lower.includes(":11434") ||
    lower.includes("11434/") ||
    (lower.includes("connection") &&
      (lower.includes("refused") || lower.includes("failed")) &&
      lower.includes("11434")) ||
    lower.includes("response ended before the assistant finished") ||
    lower.includes("no response stream available") ||
    (lower.includes("chat failed") && lower.includes("connect"))
  );
}

function matchesQdrantFailure(lower: string): boolean {
  return (
    lower.includes("qdrant") ||
    lower.includes(":6333") ||
    lower.includes("6333/") ||
    (lower.includes("indexing failed") &&
      (lower.includes("connect") ||
        lower.includes("refused") ||
        lower.includes("unavailable") ||
        lower.includes("timeout")))
  );
}

function matchesUrlValidationFailure(lower: string): boolean {
  return (
    lower.includes("youtube_url must") ||
    lower.includes("instagram_url must") ||
    lower.includes("unsupportedurl") ||
    lower.includes("unsupported url") ||
    lower.includes("could not parse youtube") ||
    lower.includes("could not parse instagram")
  );
}

function matchesYtDlpOrMetadataFailure(lower: string): boolean {
  return (
    lower.includes("yt-dlp") ||
    lower.includes("metadata extraction") ||
    lower.includes("metadata failed") ||
    lower.includes("audio download failed") ||
    lower.includes("audio file not found")
  );
}

function matchesTranscriptFailure(lower: string): boolean {
  return (
    lower.includes("transcript") ||
    lower.includes("whisper") ||
    lower.includes("ffmpeg")
  );
}

function enhanceByMessage(raw: string, context: "ingest" | "index" | "chat"): string {
  const text = raw.trim();
  const lower = text.toLowerCase();

  if (matchesOllamaFailure(lower)) {
    return ollamaUnavailableGuidance(text);
  }

  if (context === "index" && matchesQdrantFailure(lower)) {
    return qdrantUnavailableGuidance(text);
  }

  if (context === "chat" && lower.includes("session is not indexed")) {
    return formatRecoveryGuidance(
      "Chat ran before transcript evidence was indexed.",
      "Analyze did not finish the Index step, or the session was reset after extraction.",
      "Click Analyze and wait until the progress banner shows Ready with chunks indexed, then ask your question again.",
    );
  }

  if (context === "chat" && lower.includes("session not found")) {
    return formatRecoveryGuidance(
      "The chat session no longer exists on the server.",
      "The backend was restarted or session files under backend/data/sessions were removed after you analyzed.",
      "Run Analyze again with your YouTube and Instagram URLs, wait for Ready, then retry chat.",
    );
  }

  if (matchesUrlValidationFailure(lower)) {
    return formatRecoveryGuidance(
      "One or both video URLs were rejected before extraction started.",
      text,
      "Paste a full public YouTube watch URL (https://www.youtube.com/watch?v=…) and a public Instagram Reel URL (/reel/… or /reels/…), then click Analyze.",
    );
  }

  if (context === "ingest" && matchesYtDlpOrMetadataFailure(lower)) {
    return formatRecoveryGuidance(
      "Metadata or media download failed during extraction (ingest).",
      `${text} This often means the video is private, geo-blocked, removed, or temporarily unavailable to yt-dlp.`,
      "Confirm both links open in a logged-out browser, try different public URLs, ensure FFmpeg is on PATH for Reels, then click Analyze again.",
    );
  }

  if (context === "ingest" && matchesTranscriptFailure(lower)) {
    return formatRecoveryGuidance(
      "A transcript could not be produced for one or both videos.",
      `${text} Whisper or caption fallback may fail on missing audio, corrupt downloads, or very noisy tracks.`,
      "Retry with videos that have clear speech and public access; on Windows install FFmpeg (`winget install ffmpeg`) if Reel audio is required, then run Analyze again.",
    );
  }

  if (context === "ingest" && lower.includes("ingestion failed")) {
    return formatRecoveryGuidance(
      "Video extraction (ingest) did not complete for both platforms.",
      text,
      "Verify both URLs are public, the backend terminal shows the underlying error, fix FFmpeg or network issues if shown, then click Analyze again.",
    );
  }

  if (context === "index" && lower.includes("indexing failed")) {
    if (matchesQdrantFailure(lower)) {
      return qdrantUnavailableGuidance(text);
    }
    return formatRecoveryGuidance(
      "Transcript indexing did not complete.",
      text,
      "Ensure Qdrant is running (`docker compose up -d` from the repo root), confirm backend/.env QDRANT_URL matches, then click Analyze again.",
    );
  }

  if (context === "index" && lower.includes("session not found")) {
    return formatRecoveryGuidance(
      "Indexing could not find the analysis session.",
      "The server lost session data (restart, cleared backend/data/sessions, or a mismatched session id).",
      "Run Analyze again from the beginning with both URLs.",
    );
  }

  if (context === "chat" && lower.includes("chat failed")) {
    return formatRecoveryGuidance(
      "The chat request failed on the server.",
      text,
      "Check the backend terminal for details; if the message mentions Ollama or Qdrant, fix those services first, then retry your question.",
    );
  }

  return "";
}

function isApiError(err: unknown): err is Error & { status: number } {
  return err instanceof Error && err.name === "ApiError";
}

function resolveRawMessage(err: unknown, fallback: string): string {
  if (isNetworkError(err)) return "";
  if (isApiError(err)) return err.message;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

export function friendlyIngestError(err: unknown): string {
  if (isNetworkError(err)) return apiUnreachableGuidance();
  const raw = resolveRawMessage(err, "Ingestion failed.");
  const enhanced = enhanceByMessage(raw, "ingest");
  if (enhanced) return enhanced;
  return formatRecoveryGuidance(
    "Video extraction (ingest) did not complete.",
    raw,
    "Use public YouTube and Instagram Reel URLs, confirm the backend is running, review the backend terminal output, then click Analyze again.",
  );
}

export function friendlyIndexError(err: unknown): string {
  if (isNetworkError(err)) return apiUnreachableGuidance();
  const raw = resolveRawMessage(err, "Indexing failed.");
  const enhanced = enhanceByMessage(raw, "index");
  if (enhanced) return enhanced;
  return formatRecoveryGuidance(
    "Transcript indexing did not complete.",
    raw,
    "Start Qdrant with `docker compose up -d` from the repo root, verify QDRANT_URL in backend/.env, then click Analyze again.",
  );
}

export function friendlyChatError(errOrMessage: unknown): string {
  if (isNetworkError(errOrMessage)) return apiUnreachableGuidance();
  const raw =
    typeof errOrMessage === "string"
      ? errOrMessage
      : resolveRawMessage(errOrMessage, "Chat failed.");
  const enhanced = enhanceByMessage(raw, "chat");
  if (enhanced) return enhanced;
  return formatRecoveryGuidance(
    "Streaming chat did not finish successfully.",
    raw,
    "Confirm Analyze reached Ready, Ollama is running (`ollama serve` and `ollama pull llama3.2`), and the backend terminal has no errors—then send your question again.",
  );
}

/** @deprecated Use context-specific helpers; kept for generic fallbacks. */
export function friendlyErrorMessage(err: unknown, fallback: string): string {
  if (isNetworkError(err)) return apiUnreachableGuidance();
  const raw = resolveRawMessage(err, fallback);
  const enhanced =
    enhanceByMessage(raw, "chat") ||
    enhanceByMessage(raw, "index") ||
    enhanceByMessage(raw, "ingest");
  if (enhanced) return enhanced;
  return formatRecoveryGuidance(
    "The request did not succeed.",
    raw,
    "Check that the backend, Qdrant, and Ollama are running, review the backend logs, then retry.",
  );
}
