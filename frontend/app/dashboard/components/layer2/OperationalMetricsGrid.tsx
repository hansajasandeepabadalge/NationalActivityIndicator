'use client';

import React from 'react';
import { useOperationalIndicators } from '@/hooks/useDashboard';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';
import { OperationalIndicatorCard } from '../layer3/OperationalIndicatorCard';

export function OperationalMetricsGrid() {
    const { data: indicators, isLoading } = useOperationalIndicators(50);

    if (isLoading) return <LoadingSkeleton rows={5} variant="card" />;

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6 flex-shrink-0">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <span>⚙️</span> Operational Metrics (Layer 3)
                </h3>
            </div>

            <div className="pr-2 -mr-2">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {indicators && indicators.length > 0 ? (
                        indicators.map((indicator, index) => (
                            <OperationalIndicatorCard
                                key={`${indicator.indicator_id}-${index}`}
                                indicator={indicator}
                            />
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
