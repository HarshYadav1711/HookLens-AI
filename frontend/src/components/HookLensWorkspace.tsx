"use client";

import { useCallback, useRef, useState } from "react";
import { ApiError, indexSession, ingestVideos, streamChat } from "@/lib/api";
import { friendlyChatError, friendlyIngestError, friendlyIndexError } from "@/lib/errors";
import type {
  AnalysisPhase,
  ChatMessage,
  Citation,
  NormalizedVideo,
} from "@/lib/types";
import { AnalysisSummary } from "@/components/AnalysisSummary";
import { ChatPanel } from "@/components/ChatPanel";
import { ProgressBanner } from "@/components/ProgressBanner";
import { TranscriptView } from "@/components/TranscriptView";
import { UrlBar } from "@/components/UrlBar";
import { VideoCard } from "@/components/VideoCard";

function uid(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

const STATUS_MESSAGES: Record<Exclude<AnalysisPhase, "idle" | "error" | "ready">, string> = {
  extracting:
    "Downloading metadata and transcripts from both platforms. First run can take 1–2 minutes.",
  indexing: "Chunking transcripts and writing vectors to Qdrant for evidence retrieval.",
};

export function HookLensWorkspace() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [instagramUrl, setInstagramUrl] = useState("");
  const [phase, setPhase] = useState<AnalysisPhase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [youtube, setYoutube] = useState<NormalizedVideo | null>(null);
  const [instagram, setInstagram] = useState<NormalizedVideo | null>(null);
  const [chunksIndexed, setChunksIndexed] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const loading = phase === "extracting" || phase === "indexing";
  const ready = phase === "ready";

  const loadingLabel =
    phase === "extracting" ? "Extracting…" : phase === "indexing" ? "Indexing…" : "Analyze";

  const statusMessage =
    phase === "extracting" || phase === "indexing" ? STATUS_MESSAGES[phase] : null;

  const handleAnalyze = useCallback(async () => {
    setError(null);
    setMessages([]);
    setChunksIndexed(null);
    setYoutube(null);
    setInstagram(null);
    setSessionId(null);

    let extracted = false;

    try {
      setPhase("extracting");
      const ingest = await ingestVideos(youtubeUrl, instagramUrl);
      extracted = true;
      setSessionId(ingest.session_id);
      setYoutube(ingest.youtube);
      setInstagram(ingest.instagram);

      setPhase("indexing");
      const index = await indexSession(ingest.session_id);
      setChunksIndexed(index.chunks_indexed);
      setPhase("ready");
    } catch (err) {
      setPhase("error");
      setError(extracted ? friendlyIndexError(err) : friendlyIngestError(err));
    }
  }, [youtubeUrl, instagramUrl]);

  const handleSend = useCallback(
    async (text: string) => {
      if (!sessionId || !ready) return;

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      const userMsg: ChatMessage = { id: uid(), role: "user", content: text };
      const assistantId = uid();
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        citations: [],
        streaming: true,
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setStreaming(true);

      let citations: Citation[] = [];
      let finished = false;

      const finishAssistant = (patch: Partial<ChatMessage>) => {
        if (finished) return;
        finished = true;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, ...patch, streaming: false } : m,
          ),
        );
      };

      try {
        await streamChat(
          sessionId,
          text,
          {
            onCitations: (cites) => {
              citations = cites;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, citations: cites } : m,
                ),
              );
            },
            onToken: (token) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: m.content + token }
                    : m,
                ),
              );
            },
            onDone: (content) => {
              finishAssistant({
                content: content || undefined,
                citations,
              });
            },
            onError: (message) => {
              finishAssistant({ error: message, citations });
            },
          },
          controller.signal,
        );
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        finishAssistant({
          error: friendlyChatError(err),
          citations,
        });
      } finally {
        setStreaming(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId && m.streaming
              ? { ...m, streaming: false, citations: m.citations ?? citations }
              : m,
          ),
        );
      }
    },
    [sessionId, ready],
  );

  const showResults = youtube && instagram;

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-[var(--border)]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              Hook<span className="text-accent">Lens</span> AI
            </h1>
            <p className="text-xs text-[var(--muted)] mt-0.5">
              Compare YouTube vs Instagram with cited evidence
            </p>
          </div>
          {ready && sessionId && (
            <span className="hidden sm:inline text-xs font-mono text-[var(--muted)]">
              session {sessionId.slice(0, 8)}…
            </span>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6">
        <div className="space-y-5">
          <UrlBar
            youtubeUrl={youtubeUrl}
            instagramUrl={instagramUrl}
            onYoutubeChange={setYoutubeUrl}
            onInstagramChange={setInstagramUrl}
            onAnalyze={handleAnalyze}
            loading={loading}
            loadingLabel={loadingLabel}
            disabled={streaming}
          />

          <ProgressBanner
            phase={phase}
            error={error}
            chunksIndexed={chunksIndexed}
            statusMessage={statusMessage}
          />

          {showResults && (
            <div className="animate-fade-in space-y-5">
              <div className="grid gap-4 md:grid-cols-2">
                <VideoCard video={youtube} label="A" />
                <VideoCard video={instagram} label="B" />
              </div>

              <div className="grid gap-5 lg:grid-cols-[1fr_380px] lg:items-start">
                <div className="space-y-5">
                  <AnalysisSummary youtube={youtube} instagram={instagram} />
                  <TranscriptView youtube={youtube} instagram={instagram} />
                </div>

                <div className="lg:sticky lg:top-6 lg:h-[calc(100vh-8rem)]">
                  <ChatPanel
                    messages={messages}
                    onSend={handleSend}
                    disabled={!ready}
                    streaming={streaming}
                  />
                </div>
              </div>
            </div>
          )}

          {phase === "idle" && !showResults && (
            <div className="rounded-xl border border-dashed border-[var(--border)] px-6 py-16 text-center">
              <p className="text-sm text-[var(--muted)] max-w-md mx-auto">
                Paste a public YouTube URL and Instagram Reel URL, then run Analyze.
                HookLens extracts metadata and transcripts, indexes evidence, and answers
                comparison questions with numbered citations.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
