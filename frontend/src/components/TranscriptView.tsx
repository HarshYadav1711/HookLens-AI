"use client";

import { useState } from "react";
import type { NormalizedVideo } from "@/lib/types";
import { formatTimestamp } from "@/lib/format";

interface TranscriptViewProps {
  youtube: NormalizedVideo;
  instagram: NormalizedVideo;
}

type Tab = "A" | "B";

export function TranscriptView({ youtube, instagram }: TranscriptViewProps) {
  const [tab, setTab] = useState<Tab>("A");
  const video = tab === "A" ? youtube : instagram;
  const label = tab === "A" ? "YouTube (A)" : "Instagram (B)";

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--card)]">
      <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
          Transcript
        </h2>
        <div className="flex rounded-lg border border-[var(--border)] p-0.5">
          {(["A", "B"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                tab === t
                  ? "bg-accent/20 text-accent"
                  : "text-[var(--muted)] hover:text-[var(--text)]"
              }`}
            >
              Video {t}
            </button>
          ))}
        </div>
      </div>

      <div className="max-h-64 overflow-y-auto p-4 scrollbar-thin">
        {video.transcript.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">
            No transcript available for {label}.
          </p>
        ) : (
          <div className="space-y-3">
            {video.transcript.map((seg, i) => (
              <div key={i} className="flex gap-3 text-sm">
                <time
                  className="shrink-0 font-mono text-xs text-accent/80 pt-0.5"
                  dateTime={`PT${seg.start_seconds}S`}
                >
                  {formatTimestamp(seg.start_seconds)}
                </time>
                <p className="text-[var(--text)]/90 leading-relaxed">{seg.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
