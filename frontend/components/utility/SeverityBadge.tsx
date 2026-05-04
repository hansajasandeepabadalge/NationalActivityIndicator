type SeverityBadgeProps = {
    severity: string;
    size?: "sm" | "md";
};

export default function SeverityBadge({ severity, size = "md" }: SeverityBadgeProps) {
    const colors: Record<string, string> = {
        critical: "bg-red-500/20 text-red-400 border-red-500/30",
        high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
        medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    };

    const sizeClasses =
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";

    return (
        <span
            className={`${colors[severity]} ${sizeClasses} rounded-full border font-medium uppercase tracking-wide`}
        >
            {severity}
        </span>
    );
}
