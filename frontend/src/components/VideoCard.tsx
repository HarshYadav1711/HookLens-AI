import Image from "next/image";
import type { NormalizedVideo, VideoLabel } from "@/lib/types";
import {
  formatDate,
  formatDuration,
  formatNumber,
  formatEngagementRate,
  transcriptSourceLabel,
} from "@/lib/format";
import { StatusBadge, statusVariant } from "./StatusBadge";

interface VideoCardProps {
  video: NormalizedVideo;
  label: VideoLabel;
}

function thumbnailUrl(video: NormalizedVideo): string | null {
  if (video.platform === "youtube" && video.video_id) {
    return `https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg`;
  }
  return null;
}

export function VideoCard({ video, label }: VideoCardProps) {
  const thumb = thumbnailUrl(video);
  const platformLabel = label === "A" ? "YouTube" : "Instagram";

  return (
    <article className="flex flex-col overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--card)]">
      <div className="relative aspect-video bg-[var(--bg)]">
        {thumb ? (
          <Image
            src={thumb}
            alt={video.title ?? `${platformLabel} video`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 50vw"
            unoptimized
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-gradient-to-br from-[var(--border)]/40 to-[var(--bg)]">
            <span className="text-sm text-[var(--muted)]">{platformLabel}</span>
          </div>
        )}
        <div className="absolute left-2 top-2">
          <span className="rounded-md bg-black/70 px-2 py-0.5 text-xs font-medium text-white">
            Video {label} · {platformLabel}
          </span>
        </div>
        {video.duration_seconds != null && (
          <div className="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-xs text-white">
            {formatDuration(video.duration_seconds)}
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-3 p-4">
        <div>
          <h3 className="line-clamp-2 text-sm font-semibold leading-snug">
            {video.title ?? "Untitled"}
          </h3>
          {video.creator && (
            <p className="mt-0.5 text-xs text-[var(--muted)]">{video.creator}</p>
          )}
        </div>

        <dl className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-md bg-[var(--bg)] px-2 py-1.5">
            <dt className="text-[10px] uppercase tracking-wide text-[var(--muted)]">Views</dt>
            <dd className="text-sm font-medium">{formatNumber(video.views)}</dd>
          </div>
          <div className="rounded-md bg-[var(--bg)] px-2 py-1.5">
            <dt className="text-[10px] uppercase tracking-wide text-[var(--muted)]">Likes</dt>
            <dd className="text-sm font-medium">{formatNumber(video.likes)}</dd>
          </div>
          <div className="rounded-md bg-[var(--bg)] px-2 py-1.5">
            <dt className="text-[10px] uppercase tracking-wide text-[var(--muted)]">Engagement</dt>
            <dd className="text-sm font-medium">{formatEngagementRate(video.engagement_rate)}</dd>
          </div>
        </dl>

        <div className="flex flex-wrap gap-1.5">
          <StatusBadge
            label={`Metadata: ${video.metadata_status}`}
            variant={statusVariant(video.metadata_status)}
          />
          <StatusBadge
            label={`Transcript: ${video.transcript_status}`}
            variant={statusVariant(video.transcript_status)}
          />
        </div>

        <p className="text-xs text-[var(--muted)]">
          Source: {transcriptSourceLabel(video.transcript_source)}
          {video.upload_date && ` · ${formatDate(video.upload_date)}`}
        </p>

        {video.warnings.length > 0 && (
          <ul className="space-y-1 border-t border-[var(--border)] pt-2">
            {video.warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-400/90">
                {w}
              </li>
            ))}
          </ul>
        )}

        <a
          href={video.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto text-xs text-accent hover:underline"
        >
          Open original →
        </a>
      </div>
    </article>
  );
}
