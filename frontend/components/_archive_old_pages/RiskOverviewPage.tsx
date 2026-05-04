"use client";

import { Check, ChevronDown, DollarSign, Download, Search } from "lucide-react";
import { useState } from "react";
import StatCard from "@/components/utility/StatCard";
import SeverityBadge from "@/components/utility/SeverityBadge";
import { mockRisks } from "@/data/mockRisks";
import { Risk, Severity } from "@/types/risk";

export default function RiskOverviewPage() {
    const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
    const [searchQuery, setSearchQuery] = useState("");

    const filteredRisks = mockRisks.filter((risk: Risk) => {
        if (severityFilter !== "all" && risk.severity !== severityFilter) return false;
        if (searchQuery && !risk.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
        return true;
    });

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Risk Overview</h1>
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                    Export
                </button>
            </div>

            {/* Risk Summary */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="Critical Risks" value={2} color="bg-red-500/10 border-red-500/20" />
                <StatCard label="High Risks" value={5} color="bg-orange-500/10 border-orange-500/20" />
                <StatCard label="Medium Risks" value={8} color="bg-yellow-500/10 border-yellow-500/20" />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                <div className="relative">
                    <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value as Severity | "all")}
                        className="appearance-none bg-slate-700 text-white px-4 py-2 pr-10 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500"
                    >
                        <option value="all">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>

                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search risks..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-slate-700 text-white pl-10 pr-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500"
                    />
                </div>
            </div>

            {/* Risk Cards */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white">Active Risks ({filteredRisks.length})</h2>

                {filteredRisks.map((risk) => (
                    <div key={risk.id} className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6 hover:border-slate-600 transition-colors">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <SeverityBadge severity={risk.severity} />
                                <h3 className="text-lg font-semibold text-white">{risk.name}</h3>
                            </div>
                            {risk.acknowledged && (
                                <span className="text-xs text-slate-500 flex items-center gap-1">
                                    <Check className="w-3 h-3" /> Acknowledged
                                </span>
                            )}
                        </div>

                        <p className="text-slate-400 mb-4">{risk.description}</p>

                        <div className="grid grid-cols-4 gap-4 mb-4">
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Probability</p>
                                <p className="text-white font-semibold">{risk.probability}%</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Impact</p>
                                <p className="text-white font-semibold">{risk.impact}</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Time Horizon</p>
                                <p className="text-white font-semibold">{risk.timeHorizon}</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Confidence</p>
                                <p className="text-white font-semibold">{risk.confidence}%</p>
                            </div>
                        </div>

                        {risk.affectedOperations && (
                            <div className="mb-4">
                                <p className="text-xs text-slate-500 mb-2">Affected Operations:</p>
                                <div className="flex flex-wrap gap-2">
                                    {risk.affectedOperations.map((op, i) => (
                                        <span key={i} className="text-sm text-slate-300 bg-slate-700/50 px-3 py-1 rounded-full">
                                            {op.name} <span className="text-slate-500">({op.impact})</span>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {risk.financialImpact && (
                            <div className="mb-4 p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
                                <p className="text-sm text-orange-400">
                                    <DollarSign className="w-4 h-4 inline mr-1" />
                                    Financial Impact Estimate: {risk.financialImpact}
                                </p>
                            </div>
                        )}

                        <div className="flex items-center gap-3 pt-4 border-t border-slate-700">
                            <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium">
                                View Full Analysis
                            </button>
                            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium">
                                See Recommendations
                            </button>
                            {!risk.acknowledged && (
                                <button className="px-4 py-2 text-slate-400 hover:text-white transition-colors text-sm">
                                    Mark as Acknowledged
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
