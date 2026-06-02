import type { AnalysisPhase } from "@/lib/types";

interface ProgressBannerProps {
  phase: AnalysisPhase;
  error?: string | null;
  chunksIndexed?: number | null;
  statusMessage?: string | null;
}

const steps: { key: AnalysisPhase; label: string }[] = [
  { key: "extracting", label: "Extract" },
  { key: "indexing", label: "Index" },
  { key: "ready", label: "Ready" },
];

function stepIndex(phase: AnalysisPhase): number {
  if (phase === "idle" || phase === "error") return -1;
  if (phase === "extracting") return 0;
  if (phase === "indexing") return 1;
  return 2;
}

export function ProgressBanner({
  phase,
  error,
  chunksIndexed,
  statusMessage,
}: ProgressBannerProps) {
  if (phase === "idle") return null;

  const active = stepIndex(phase);

  return (
    <div
      role="status"
      aria-live="polite"
      className={`rounded-lg border px-4 py-3 ${
        phase === "error"
          ? "border-red-500/40 bg-red-500/10"
          : "border-[var(--border)] bg-[var(--card)]"
      }`}
    >
      {phase === "error" ? (
        <div className="space-y-1">
          <p className="text-sm font-medium text-red-400">Analysis could not complete</p>
          <p className="whitespace-pre-wrap text-sm text-red-400/90">
            {error ?? "Something went wrong."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <div className="flex items-center gap-3">
              {steps.map((step, i) => {
                const done = active > i;
                const current = active === i;
                return (
                  <div key={step.key} className="flex items-center gap-2">
                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium ${
                        done
                          ? "bg-emerald-500/20 text-emerald-400"
                          : current
                            ? "bg-accent/20 text-accent"
                            : "bg-[var(--border)] text-[var(--muted)]"
                      }`}
                    >
                      {done ? "✓" : current ? (
                        <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                      ) : (
                        i + 1
                      )}
                    </span>
                    <span
                      className={`text-sm ${
                        current ? "text-[var(--text)] font-medium" : "text-[var(--muted)]"
                      }`}
                    >
                      {step.label}
                    </span>
                    {i < steps.length - 1 && (
                      <span className="ml-1 text-[var(--border)]">→</span>
                    )}
                  </div>
                );
              })}
            </div>
            {phase === "ready" && chunksIndexed != null && (
              <span className="text-xs text-emerald-400/90">
                {chunksIndexed} evidence chunks indexed — chat is ready
              </span>
            )}
          </div>
          {statusMessage && phase !== "ready" && (
            <p className="text-xs text-[var(--muted)]">{statusMessage}</p>
          )}
        </div>
      )}
    </div>
  );
}
