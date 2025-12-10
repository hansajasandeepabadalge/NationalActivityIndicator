'use client';

import React from 'react';
import { TrendArrow } from '../shared/Badge';
import { useOperationalIndicators } from '@/hooks/useDashboard';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

export function OperationalMetricsGrid() {
    const { data: indicators, isLoading } = useOperationalIndicators(50);

    if (isLoading) return <LoadingSkeleton rows={5} variant="card" />;

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <span>⚙️</span> Operational Metrics (Layer 3)
                </h3>
            </div>

            <div className="flex-1 overflow-y-auto pr-2">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
                    {indicators && indicators.length > 0 ? (
                        indicators.map((indicator, index) => (
                            <div
                                key={`${indicator.indicator_id}-${index}`}
                                className="p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all group"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-[10px] font-bold uppercase tracking-wider rounded">
                                        {indicator.category}
                                    </span>
                                    <TrendArrow trend={indicator.trend || 'stable'} />
                                </div>

                                <h4 className="text-sm font-medium text-gray-900 line-clamp-2 mb-3 h-10" title={indicator.indicator_name}>
                                    {indicator.indicator_name}
                                </h4>

                                <div className="flex items-baseline justify-between pt-2 border-t border-gray-100">
                                    <span className="text-xs text-gray-500">Current Value</span>
                                    <span className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                        {indicator.current_value?.toLocaleString() ?? 'N/A'}
                                    </span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-8 text-gray-400">
                            No operational metrics available.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
