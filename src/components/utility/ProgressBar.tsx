import React from "react";
type ProgressBarProps = {
    value: number;
    color?: string;
};

export default function ProgressBar({ value, color }:ProgressBarProps) {
    const getColor = () => {
        if (color) return color;
        if (value >= 80) return "bg-emerald-500";
        if (value >= 60) return "bg-yellow-500";
        return "bg-red-500";
    };

    return (
        <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
                className={`h-full ${getColor()} transition-all duration-500`}
                style={{ width: `${value}%` }}
            />
        </div>
    );
};
