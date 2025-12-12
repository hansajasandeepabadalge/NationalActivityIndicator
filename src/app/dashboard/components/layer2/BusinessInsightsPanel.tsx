'use client';

import React from 'react';
import { SeverityBadge } from '../shared/Badge';
import { useBusinessInsights } from '@/hooks/useDashboard';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

export function BusinessInsightsPanel() {
    const { data: insights, isLoading } = useBusinessInsights(undefined, undefined, undefined, 20);

    if (isLoading) return <LoadingSkeleton rows={5} variant="card" />;

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <span>💡</span> Business Insights (Layer 4)
                </h3>
                {insights && (
                    <span className="flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-md">
                        <span>⚠️</span> {insights.filter(i => i.severity_level === 'high' || i.severity_level === 'critical').length} Critical
                    </span>
                )}
            </div>

            <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                {insights && insights.length > 0 ? (
                    insights.map((insight) => (
                        <div
                            key={insight.insight_id}
                            className="relative p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 shadow-sm hover:shadow-md transition-all overflow-hidden group"
                        >
                            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-400 to-blue-500 opacity-80" />

                            <div className="pl-3">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">{insight.insight_type}</span>
                                        <span className="text-xs text-gray-300">•</span>
                                        <span className="text-xs text-gray-500">{(insight as any).timestamp ? new Date((insight as any).timestamp).toLocaleDateString() : 'Just now'}</span>
                                    </div>
                                    <SeverityBadge level={insight.severity_level || 'medium'} />
                                </div>

                                <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-purple-700 transition-colors">
                                    {insight.title}
                                </h4>

                                <p className="text-sm text-gray-600 leading-relaxed mb-3">
                                    {insight.description}
                                </p>

                                {(insight as any).confidence_score && (
                                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-dashed border-gray-100">
                                        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-purple-500 rounded-full"
                                                style={{ width: `${(insight as any).confidence_score * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-xs font-medium text-purple-600">
                                            {((insight as any).confidence_score * 100).toFixed(0)}% Confidence
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-12 text-gray-400">
                        No active business insights at this time.
                    </div>
                )}
            </div>
        </div>
    );
}
