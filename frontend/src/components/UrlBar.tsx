"use client";

interface UrlBarProps {
  youtubeUrl: string;
  instagramUrl: string;
  onYoutubeChange: (value: string) => void;
  onInstagramChange: (value: string) => void;
  onAnalyze: () => void;
  loading: boolean;
  disabled: boolean;
}

export function UrlBar({
  youtubeUrl,
  instagramUrl,
  onYoutubeChange,
  onInstagramChange,
  onAnalyze,
  loading,
  disabled,
}: UrlBarProps) {
  const canSubmit =
    !loading &&
    !disabled &&
    youtubeUrl.trim().length > 0 &&
    instagramUrl.trim().length > 0;

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
      <label className="flex-1 space-y-1.5">
        <span className="text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
          YouTube · Video A
        </span>
        <input
          type="url"
          value={youtubeUrl}
          onChange={(e) => onYoutubeChange(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          disabled={loading}
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2.5 text-sm placeholder:text-[var(--muted)]/60 focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50"
        />
      </label>
      <label className="flex-1 space-y-1.5">
        <span className="text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
          Instagram Reel · Video B
        </span>
        <input
          type="url"
          value={instagramUrl}
          onChange={(e) => onInstagramChange(e.target.value)}
          placeholder="https://www.instagram.com/reel/..."
          disabled={loading}
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2.5 text-sm placeholder:text-[var(--muted)]/60 focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50"
        />
      </label>
      <button
        type="button"
        onClick={onAnalyze}
        disabled={!canSubmit}
        className="shrink-0 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? "Analyzing…" : "Analyze"}
      </button>
    </div>
  );
}
