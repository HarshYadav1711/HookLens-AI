interface StatusBadgeProps {
  label: string;
  variant: "success" | "warning" | "error" | "neutral";
}

const variants: Record<StatusBadgeProps["variant"], string> = {
  success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  error: "bg-red-500/15 text-red-400 border-red-500/30",
  neutral: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

export function StatusBadge({ label, variant }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${variants[variant]}`}
    >
      {label}
    </span>
  );
}

export function statusVariant(
  status: string,
): StatusBadgeProps["variant"] {
  if (status === "complete" || status === "available") return "success";
  if (status === "partial") return "warning";
  if (status === "failed" || status === "unavailable") return "error";
  return "neutral";
}
