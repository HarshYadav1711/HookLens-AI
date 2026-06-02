import type { Citation } from "@/lib/types";
import { formatTimestamp, videoLabelName } from "@/lib/format";

interface CitationsListProps {
  citations: Citation[];
}

export function CitationsList({ citations }: CitationsListProps) {
  return (
    <div className="mt-3 border-t border-[var(--border)] pt-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
        Sources {citations.length > 0 ? `(${citations.length})` : ""}
      </p>
      {citations.length === 0 ? (
        <p className="text-xs text-[var(--muted)]">No transcript evidence cited for this answer.</p>
      ) : (
      <ol className="space-y-2">
        {citations.map((cite) => (
          <li
            key={`${cite.chunk_id}-${cite.index}`}
            className="rounded-lg border border-[var(--border)] bg-[var(--bg)] p-2.5"
          >
            <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
              <span className="inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded bg-accent/20 px-1 text-xs font-semibold text-accent">
                [{cite.index}]
              </span>
              <span className="text-xs font-medium">
                {videoLabelName(cite.video_label)}
              </span>
              <span className="text-xs text-[var(--muted)]">
                {formatTimestamp(cite.start_time)}–{formatTimestamp(cite.end_time)}
              </span>
              {cite.score > 0 && (
                <span className="text-xs text-[var(--muted)]">
                  relevance {(cite.score * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p className="mt-1.5 text-xs leading-relaxed text-[var(--text)]/80 line-clamp-3">
              {cite.excerpt}
            </p>
            {cite.url && (
              <a
                href={cite.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 inline-block text-xs text-accent hover:underline"
              >
                View video →
              </a>
            )}
          </li>
        ))}
      </ol>
      )}
    </div>
  );
}
