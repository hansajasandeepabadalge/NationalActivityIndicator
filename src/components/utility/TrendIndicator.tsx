import { ArrowUp, Minus, ArrowDown } from "lucide-react";

type TrendIndicatorProps = {
    trend: "up" | "down" | "stable";
};

export default function TrendIndicator({ trend }: TrendIndicatorProps) {
    if (trend === "up") return <ArrowUp className="w-4 h-4 text-emerald-400" />;
    if (trend === "down") return <ArrowDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
}
