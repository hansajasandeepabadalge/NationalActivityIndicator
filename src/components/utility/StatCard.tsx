import React from "react";

type StatCardProps = {
    label: string;
    value: string | number;
    color?: string;
};

export default function StatCard({ label, value, color = "bg-slate-800" }: StatCardProps) {
    return (
        <div className={`${color} rounded-xl p-4 border border-slate-700/50`}>
            <div className="text-2xl font-bold text-white mb-1">{value}</div>
            <div className="text-sm text-slate-400">{label}</div>
        </div>
    );
}
