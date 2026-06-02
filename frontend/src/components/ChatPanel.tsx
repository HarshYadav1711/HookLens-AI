"use client";

import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "@/lib/types";
import { CitationsList } from "./CitationsList";

interface ChatPanelProps {
  messages: ChatMessage[];
  onSend: (message: string) => void;
  disabled: boolean;
  streaming: boolean;
}

export function ChatPanel({ messages, onSend, disabled, streaming }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled || streaming) return;
    onSend(trimmed);
    setInput("");
  }

  return (
    <section className="flex h-full min-h-[420px] flex-col rounded-xl border border-[var(--border)] bg-[var(--card)] lg:min-h-0">
      <header className="border-b border-[var(--border)] px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
          Ask HookLens
        </h2>
        <p className="mt-0.5 text-xs text-[var(--muted)]">
          Evidence-backed answers with citations
        </p>
      </header>

      <div ref={listRef} className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex h-full min-h-[200px] items-center justify-center text-center">
            <div className="max-w-xs">
              <p className="text-sm text-[var(--muted)]">
                {disabled
                  ? "Run analysis first, then ask about hooks, pacing, or performance."
                  : "Compare hooks, openings, or engagement drivers between both videos."}
              </p>
              {!disabled && (
                <ul className="mt-3 space-y-1 text-left text-xs text-[var(--muted)]/80">
                  <li>· What happens in the first 3 seconds?</li>
                  <li>· Which video has a stronger hook?</li>
                  <li>· Compare call-to-action timing</li>
                </ul>
              )}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[92%] rounded-xl px-3.5 py-2.5 ${
                msg.role === "user"
                  ? "bg-accent/20 text-[var(--text)]"
                  : "bg-[var(--bg)] border border-[var(--border)]"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {msg.content}
                {msg.streaming && (
                  <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse bg-accent/70" />
                )}
              </p>
              {msg.error && (
                <p className="mt-1 text-xs text-red-400">{msg.error}</p>
              )}
              {msg.role === "assistant" && (msg.citations?.length || !msg.streaming) && (
                <CitationsList citations={msg.citations ?? []} />
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-[var(--border)] p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={disabled ? "Analyze videos to enable chat" : "Ask a question…"}
            disabled={disabled || streaming}
            className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={disabled || streaming || !input.trim()}
            className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </section>
  );
}
