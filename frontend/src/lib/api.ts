import {
  formatApiErrorDetail,
  friendlyChatError,
  friendlyErrorMessage,
  isNetworkError,
} from "./errors";
import { parseSSEChunk } from "./sse";
import type {
  Citation,
  IngestResponse,
  IndexResponse,
  StreamEvent,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getApiBaseUrl(): string {
  return API_BASE;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseErrorResponse(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return formatApiErrorDetail(body.detail ?? body.message ?? res.statusText);
  } catch {
    return res.statusText || "Request failed";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch (err) {
    if (isNetworkError(err)) {
      throw new ApiError(friendlyErrorMessage(err, "Cannot reach the API."), 0);
    }
    throw err;
  }

  if (!res.ok) {
    throw new ApiError(await parseErrorResponse(res), res.status);
  }

  return res.json() as Promise<T>;
}

export async function ingestVideos(
  youtubeUrl: string,
  instagramUrl: string,
): Promise<IngestResponse> {
  return request<IngestResponse>("/api/ingest", {
    method: "POST",
    body: JSON.stringify({
      youtube_url: youtubeUrl.trim(),
      instagram_url: instagramUrl.trim(),
    }),
  });
}

export async function indexSession(sessionId: string): Promise<IndexResponse> {
  return request<IndexResponse>(`/api/sessions/${sessionId}/index`, {
    method: "POST",
  });
}

export interface ChatStreamCallbacks {
  onCitations: (citations: Citation[]) => void;
  onToken: (text: string) => void;
  onDone: (content: string) => void;
  onError: (message: string) => void;
}

export async function streamChat(
  sessionId: string,
  message: string,
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/sessions/${sessionId}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, thread_id: "default" }),
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    if (isNetworkError(err)) {
      callbacks.onError(friendlyChatError(err));
      return;
    }
    callbacks.onError(friendlyChatError(err instanceof Error ? err.message : "Chat request failed"));
    return;
  }

  if (!res.ok) {
    callbacks.onError(friendlyChatError(await parseErrorResponse(res)));
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    callbacks.onError(friendlyChatError("No response stream available"));
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let receivedDone = false;
  let receivedError = false;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const { events, remainder } = parseSSEChunk(buffer);
      buffer = remainder;

      for (const event of events) {
        if (event.event === "done") receivedDone = true;
        if (event.event === "error") receivedError = true;
        dispatchStreamEvent(event, callbacks);
      }
    }

    if (buffer.trim()) {
      const { events } = parseSSEChunk(buffer + "\n\n");
      for (const event of events) {
        if (event.event === "done") receivedDone = true;
        if (event.event === "error") receivedError = true;
        dispatchStreamEvent(event, callbacks);
      }
    }
  } finally {
    reader.releaseLock();
  }

  if (!receivedDone && !receivedError) {
    callbacks.onError(
      friendlyChatError(
        "Response ended before the assistant finished. Check Ollama is running (ollama serve).",
      ),
    );
  }
}

function dispatchStreamEvent(event: StreamEvent, callbacks: ChatStreamCallbacks): void {
  switch (event.event) {
    case "citations":
      callbacks.onCitations(event.data as Citation[]);
      break;
    case "token": {
      const payload = event.data as { text?: string };
      if (payload.text) callbacks.onToken(payload.text);
      break;
    }
    case "done": {
      const payload = event.data as { content?: string };
      callbacks.onDone(payload.content ?? "");
      break;
    }
    case "error": {
      const payload = event.data as { message?: string };
      callbacks.onError(friendlyChatError(payload.message ?? "Stream error"));
      break;
    }
  }
}

export { ApiError };
