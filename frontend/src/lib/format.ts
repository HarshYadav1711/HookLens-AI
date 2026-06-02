export function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null || seconds <= 0) return "—";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return m > 0 ? `${m}:${s.toString().padStart(2, "0")}` : `0:${s.toString().padStart(2, "0")}`;
}

export function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return "—";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString();
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${(value * 100).toFixed(2)}%`;
}

/** Backend stores engagement_rate as a percentage value (e.g. 6.0 = 6%). */
export function formatEngagementRate(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${value.toFixed(2)}%`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  if (/^\d{8}$/.test(value)) {
    const y = value.slice(0, 4);
    const m = value.slice(4, 6);
    const d = value.slice(6, 8);
    return `${y}-${m}-${d}`;
  }
  return value;
}

export function videoLabelName(label: "A" | "B"): string {
  return label === "A" ? "YouTube (A)" : "Instagram (B)";
}

export function transcriptSourceLabel(source: string): string {
  const labels: Record<string, string> = {
    youtube_transcript_api: "YouTube captions",
    youtube_transcript_api_auto: "YouTube auto-captions",
    faster_whisper: "Whisper transcription",
    unavailable: "Unavailable",
  };
  return labels[source] ?? source;
}
