import {
    Activity,
    Bell,
    FileText,
    TrendingUp,
    AlertTriangle,
    Settings, LucideIcon,
} from "lucide-react";

import { Shield } from "lucide-react";

type NavigationProps = {
    activePage: string;
    onNavigate: (page: string) => void;
};

export default function Navigation({ activePage, onNavigate }:NavigationProps) {
    const navItems: { id: string; icon: LucideIcon; label: string }[] = [
        { id: "risks", icon: AlertTriangle, label: "Risk Overview" },
        { id: "opportunities", icon: TrendingUp, label: "Opportunities" },
        { id: "indicators", icon: Activity, label: "Indicators" },
        { id: "alerts", icon: Bell, label: "Alerts" },
        { id: "reports", icon: FileText, label: "Reports" },
        { id: "settings", icon: Settings, label: "Settings" },
    ];

    return (
        <nav className="fixed left-0 top-0 h-full w-64 bg-slate-900 border-r border-slate-800 p-4 flex flex-col">
            <div className="flex items-center gap-3 mb-8 px-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h1 className="font-bold text-white">RiskGuard</h1>
                    <p className="text-xs text-slate-500">Business Intelligence</p>
                </div>
            </div>

            <div className="flex-1 space-y-1">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <button
                            key={item.id}
                            onClick={() => onNavigate(item.id)}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                                activePage === item.id
                                    ? "bg-indigo-600 text-white"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                            }`}
                        >
                            <Icon className="w-5 h-5" />
                            <span className="font-medium">{item.label}</span>
                            {item.id === "alerts" && (
                                <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                                    3
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>

            <div className="pt-4 border-t border-slate-800">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-white font-bold text-sm">
                        JD
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">
                            John Doe
                        </p>
                        <p className="text-xs text-slate-500">Owner</p>
                    </div>
                </div>
            </div>
        </nav>
    );
};
