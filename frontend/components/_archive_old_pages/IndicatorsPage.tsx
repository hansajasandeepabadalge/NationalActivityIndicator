"use client";
import {useState} from "react";
import {Activity, ArrowDown} from 'lucide-react';
import TrendIndicator from "@/components/utility/TrendIndicator"
import ProgressBar from "@/components/utility/ProgressBar";
import { mockIndicators } from "@/data/mockIndicators";

export default function IndicatorsPage() {
    const [filter, setFilter] = useState('all');
    const overallScore = 72;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Operational Health Indicators</h1>

            {/* Overall Status */}
            <div className="p-6 bg-gradient-to-r from-indigo-600/20 to-purple-600/20 rounded-xl border border-indigo-500/30">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-slate-400 mb-1">Overall Status</p>
                        <div className="flex items-center gap-3">
                            <span className="text-4xl font-bold text-white">{overallScore}/100</span>
                            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-sm font-medium">GOOD</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="flex items-center gap-2 text-red-400">
                            <ArrowDown className="w-4 h-4" />
                            <span className="text-sm">5 points from last week</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-xl border border-slate-700/50 w-fit">
                {['all', 'improving', 'declining', 'stable'].map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                            filter === f
                                ? 'bg-indigo-600 text-white'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        {f}
                    </button>
                ))}
            </div>

            {/* Indicator Cards */}
            <div className="space-y-4">
                {mockIndicators
                    .filter(ind => {
                        if (filter === 'all') return true;
                        if (filter === 'improving') return ind.trend === 'up';
                        if (filter === 'declining') return ind.trend === 'down';
                        if (filter === 'stable') return ind.trend === 'stable';
                        return true;
                    })
                    .map(indicator => (
                        <div key={indicator.id} className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-4">
                                    <h3 className="text-lg font-semibold text-white">{indicator.name}</h3>
                                    <span className="text-2xl font-bold text-white">{indicator.score}/100</span>
                                    {indicator.status === 'good' && <span className="text-emerald-400">✅</span>}
                                    {indicator.status === 'warning' && <span className="text-yellow-400">⚠️</span>}
                                    {indicator.status === 'critical' && <span className="text-red-400">❌</span>}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <TrendIndicator trend={indicator.trend} />
                                    <span className={`capitalize ${
                                        indicator.trend === 'up' ? 'text-emerald-400' :
                                            indicator.trend === 'down' ? 'text-red-400' : 'text-slate-400'
                                    }`}>
                    {indicator.trend === 'up' ? 'Improving' : indicator.trend === 'down' ? 'Declining' : 'Stable'}
                  </span>
                                    <span className="text-slate-500">| Last 7 days</span>
                                </div>
                            </div>

                            <div className="mb-4">
                                <ProgressBar value={indicator.score} />
                            </div>

                            <div className="space-y-3">
                                <p className="text-xs text-slate-500">Contributing Factors:</p>
                                {indicator.factors.map((factor, i) => (
                                    <div key={i} className="flex items-center gap-4">
                                        <span className="text-sm text-slate-300 w-48">{factor.name}</span>
                                        <div className="flex-1 max-w-xs">
                                            <ProgressBar value={factor.score} />
                                        </div>
                                        <span className="text-sm text-white font-medium w-16">{factor.score}/100</span>
                                        <TrendIndicator trend={factor.trend} />
                                    </div>
                                ))}
                            </div>

                            <button className="mt-4 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                                View Details →
                            </button>
                        </div>
                    ))}
            </div>

            {/* Trend Chart Placeholder */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Trend Over Time (Last 30 Days)</h3>
                <div className="h-64 flex items-center justify-center text-slate-500">
                    <div className="text-center">
                        <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Multi-line trend chart visualization</p>
                    </div>
                </div>
            </div>
        </div>
    );
};