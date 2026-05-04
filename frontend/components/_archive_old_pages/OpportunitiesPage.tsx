import { Download, ChevronDown, Check, X, Clock } from 'lucide-react';
import StatCard from "@/components/utility/StatCard";
import ValueBadge from "@/components/utility/ValueBadge";
import { mockOpportunities } from "@/data/mockOpportunities";

export default function OpportunitiesPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Business Opportunities</h1>
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                    Export
                </button>
            </div>

            {/* Opportunity Summary */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="High Value" value={3} color="bg-emerald-500/10 border-emerald-500/20" />
                <StatCard label="Medium Value" value={5} color="bg-blue-500/10 border-blue-500/20" />
                <StatCard label="Total Active" value={11} color="bg-slate-700/50" />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                <div className="relative">
                    <select className="appearance-none bg-slate-700 text-white px-4 py-2 pr-10 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500">
                        <option>All Values</option>
                        <option>High</option>
                        <option>Medium</option>
                        <option>Low</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>

                <div className="relative">
                    <select className="appearance-none bg-slate-700 text-white px-4 py-2 pr-10 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500">
                        <option>All Categories</option>
                        <option>Financial</option>
                        <option>Operational</option>
                        <option>Strategic</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>

                <div className="relative">
                    <select className="appearance-none bg-slate-700 text-white px-4 py-2 pr-10 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500">
                        <option>Any Feasibility</option>
                        <option>High (&gt;75%)</option>
                        <option>Medium (50-75%)</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                </div>
            </div>

            {/* Opportunity Cards */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white">Active Opportunities ({mockOpportunities.length})</h2>

                {mockOpportunities.map(opp => (
                    <div key={opp.id} className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6 hover:border-slate-600 transition-colors">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">💡</span>
                                <ValueBadge value={opp.value} />
                                <h3 className="text-lg font-semibold text-white">{opp.name}</h3>
                            </div>
                        </div>

                        <p className="text-slate-400 mb-4">{opp.description}</p>

                        <div className="grid grid-cols-4 gap-4 mb-4">
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Potential Value</p>
                                <p className="text-white font-semibold">{opp.potentialValue}/10</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Feasibility</p>
                                <p className="text-white font-semibold">{opp.feasibility}%</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Strategic Fit</p>
                                <p className="text-white font-semibold">{opp.strategicFit}%</p>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">Timing</p>
                                <p className="text-white font-semibold">{opp.timing}</p>
                            </div>
                        </div>

                        <div className="mb-4 p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                            <p className="text-sm font-medium text-emerald-400 mb-1">Why Now:</p>
                            <p className="text-sm text-emerald-300/80">{opp.whyNow}</p>
                        </div>

                        <div className="mb-4">
                            <p className="text-xs text-slate-500 mb-2">Requirements:</p>
                            <div className="space-y-2">
                                {opp.requirements.map((req, i) => (
                                    <div key={i} className="flex items-center gap-2 text-sm">
                                        {req.status === 'have' ? (
                                            <Check className="w-4 h-4 text-emerald-400" />
                                        ) : (
                                            <X className="w-4 h-4 text-slate-500" />
                                        )}
                                        <span className={req.status === 'have' ? 'text-slate-300' : 'text-slate-500'}>
                      {req.item}
                    </span>
                                        <span className={`text-xs px-2 py-0.5 rounded ${req.status === 'have' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-500'}`}>
                      {req.status}
                    </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center gap-3 pt-4 border-t border-slate-700">
                            <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors text-sm font-medium">
                                I&#39;m Interested
                            </button>
                            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium">
                                View Full Details
                            </button>
                            <button className="px-4 py-2 text-slate-400 hover:text-white transition-colors text-sm">
                                Not Relevant
                            </button>
                            <button className="px-4 py-2 text-slate-400 hover:text-white transition-colors text-sm flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                Remind Me Later
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};