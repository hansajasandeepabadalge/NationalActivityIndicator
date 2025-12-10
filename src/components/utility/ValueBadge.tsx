type ValueBadgeProps = {
    value: "high" | "medium" | "low";
};

export default function ValueBadge({ value }: ValueBadgeProps) {
    const colors: Record<string, string> = {
        high: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        medium: "bg-blue-500/20 text-blue-400 border-blue-500/30",
        low: "bg-slate-500/20 text-slate-400 border-slate-500/30",
    };

    return (
        <span
            className={`${colors[value]} px-3 py-1 rounded-full border text-sm font-medium uppercase tracking-wide`}
        >
            {value} value
        </span>
    );
}
