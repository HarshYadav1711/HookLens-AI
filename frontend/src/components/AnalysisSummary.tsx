import type { NormalizedVideo } from "@/lib/types";
import {
  formatDate,
  formatDuration,
  formatNumber,
  formatEngagementRate,
} from "@/lib/format";

interface AnalysisSummaryProps {
  youtube: NormalizedVideo;
  instagram: NormalizedVideo;
}

function InsightRow({
  label,
  valueA,
  valueB,
}: {
  label: string;
  valueA: string;
  valueB: string;
}) {
  return (
    <tr className="border-b border-[var(--border)] last:border-0">
      <td className="py-2.5 pr-4 text-sm text-[var(--muted)]">{label}</td>
      <td className="py-2.5 pr-4 text-sm font-medium">{valueA}</td>
      <td className="py-2.5 text-sm font-medium">{valueB}</td>
    </tr>
  );
}

export function AnalysisSummary({ youtube, instagram }: AnalysisSummaryProps) {
  const aSegments = youtube.transcript.length;
  const bSegments = instagram.transcript.length;

  const insights: string[] = [];

  if (youtube.engagement_rate != null && instagram.engagement_rate != null) {
    const diff = instagram.engagement_rate - youtube.engagement_rate;
    const leader = diff > 0 ? "Instagram (B)" : diff < 0 ? "YouTube (A)" : "Both";
    if (leader !== "Both") {
      insights.push(
        `${leader} shows higher engagement rate (${formatEngagementRate(Math.max(youtube.engagement_rate, instagram.engagement_rate))} vs ${formatEngagementRate(Math.min(youtube.engagement_rate, instagram.engagement_rate))}).`,
      );
    }
  }

  if (youtube.duration_seconds && instagram.duration_seconds) {
    const ratio = youtube.duration_seconds / instagram.duration_seconds;
    if (ratio > 1.5) {
      insights.push(
        `YouTube (A) is ${ratio.toFixed(1)}× longer — hook pacing may differ significantly.`,
      );
    } else if (ratio < 0.67) {
      insights.push(
        `Instagram (B) is ${(1 / ratio).toFixed(1)}× longer — compare opening seconds carefully.`,
      );
    }
  }

  if (youtube.transcript_status === "unavailable" || instagram.transcript_status === "unavailable") {
    insights.push(
      "One or both transcripts are unavailable — chat answers will rely on partial evidence.",
    );
  }

  const allWarnings = [...youtube.warnings, ...instagram.warnings];
  if (allWarnings.length > 0) {
    insights.push(`${allWarnings.length} extraction warning(s) detected during ingest.`);
  }

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
        Analysis Summary
      </h2>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[320px]">
          <thead>
            <tr className="border-b border-[var(--border)] text-left">
              <th className="pb-2 pr-4 text-xs font-medium text-[var(--muted)]">Metric</th>
              <th className="pb-2 pr-4 text-xs font-medium text-accent">Video A · YouTube</th>
              <th className="pb-2 text-xs font-medium text-pink-400">Video B · Instagram</th>
            </tr>
          </thead>
          <tbody>
            <InsightRow label="Creator" valueA={youtube.creator ?? "—"} valueB={instagram.creator ?? "—"} />
            <InsightRow label="Duration" valueA={formatDuration(youtube.duration_seconds)} valueB={formatDuration(instagram.duration_seconds)} />
            <InsightRow label="Views" valueA={formatNumber(youtube.views)} valueB={formatNumber(instagram.views)} />
            <InsightRow label="Likes" valueA={formatNumber(youtube.likes)} valueB={formatNumber(instagram.likes)} />
            <InsightRow label="Comments" valueA={formatNumber(youtube.comments)} valueB={formatNumber(instagram.comments)} />
            <InsightRow label="Engagement" valueA={formatEngagementRate(youtube.engagement_rate)} valueB={formatEngagementRate(instagram.engagement_rate)} />
            <InsightRow label="Followers" valueA={formatNumber(youtube.follower_count)} valueB={formatNumber(instagram.follower_count)} />
            <InsightRow label="Uploaded" valueA={formatDate(youtube.upload_date)} valueB={formatDate(instagram.upload_date)} />
            <InsightRow label="Transcript segments" valueA={String(aSegments)} valueB={String(bSegments)} />
            <InsightRow label="Transcript status" valueA={youtube.transcript_status} valueB={instagram.transcript_status} />
          </tbody>
        </table>
      </div>

      {(youtube.hashtags?.length || instagram.hashtags?.length) ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {youtube.hashtags && youtube.hashtags.length > 0 && (
            <div>
              <p className="text-xs text-[var(--muted)] mb-1.5">YouTube hashtags</p>
              <div className="flex flex-wrap gap-1">
                {youtube.hashtags.slice(0, 8).map((tag) => (
                  <span key={tag} className="rounded bg-[var(--bg)] px-2 py-0.5 text-xs">
                    #{tag.replace(/^#/, "")}
                  </span>
                ))}
              </div>
            </div>
          )}
          {instagram.hashtags && instagram.hashtags.length > 0 && (
            <div>
              <p className="text-xs text-[var(--muted)] mb-1.5">Instagram hashtags</p>
              <div className="flex flex-wrap gap-1">
                {instagram.hashtags.slice(0, 8).map((tag) => (
                  <span key={tag} className="rounded bg-[var(--bg)] px-2 py-0.5 text-xs">
                    #{tag.replace(/^#/, "")}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}

      {insights.length > 0 && (
        <div className="mt-4 border-t border-[var(--border)] pt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-[var(--muted)] mb-2">
            Metadata insights
          </p>
          <ul className="space-y-1.5">
            {insights.map((item, i) => (
              <li key={i} className="text-sm text-[var(--text)]/90 before:content-['•'] before:mr-2 before:text-accent">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
