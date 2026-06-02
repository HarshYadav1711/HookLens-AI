import type { AnalysisPhase } from "@/lib/types";

interface ProgressBannerProps {
  phase: AnalysisPhase;
  error?: string | null;
  chunksIndexed?: number | null;
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

export function ProgressBanner({ phase, error, chunksIndexed }: ProgressBannerProps) {
  if (phase === "idle") return null;

  const active = stepIndex(phase);

  return (
    <div
      className={`rounded-lg border px-4 py-3 ${
        phase === "error"
          ? "border-red-500/40 bg-red-500/10"
          : "border-[var(--border)] bg-[var(--card)]"
      }`}
    >
      {phase === "error" ? (
        <p className="text-sm text-red-400">{error ?? "Analysis failed."}</p>
      ) : (
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
                    {done ? "✓" : i + 1}
                  </span>
                  <span
                    className={`text-sm ${
                      current ? "text-[var(--text)] font-medium" : "text-[var(--muted)]"
                    }`}
                  >
                    {step.label}
                    {current && phase === "extracting" && "…"}
                    {current && phase === "indexing" && "…"}
                  </span>
                  {i < steps.length - 1 && (
                    <span className="ml-1 text-[var(--border)]">→</span>
                  )}
                </div>
              );
            })}
          </div>
          {phase === "ready" && chunksIndexed != null && (
            <span className="text-xs text-[var(--muted)]">
              {chunksIndexed} evidence chunks indexed
            </span>
          )}
        </div>
      )}
    </div>
  );
}
