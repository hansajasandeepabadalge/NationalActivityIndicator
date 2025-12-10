'use client';

import React, { useEffect, useState } from 'react';
import { OperationalService, OperationalCalculation, operationalService } from '../../../services/operationalService';
import { OperationalIndicatorCard } from './OperationalIndicatorCard';
import { IndustryBreakdown } from './IndustryBreakdown';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

export function OperationalOverview() {
    const [indicators, setIndicators] = useState<OperationalIndicator[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [overallHealth, setOverallHealth] = useState(0);

    useEffect(() => {
        const loadData = async () => {
            try {
                // In a real app, you might get this token from context or a hook
                // For now, we assume standard flow or mock if auth not set up
                const response = await operationalService.getOperationalIndicators();
                setIndicators(response.indicators);
                setOverallHealth(operationalService.calculateOverallHealth(response.indicators));
            } catch (err) {
                console.error("Failed to load operational indicators", err);
                setError("Failed to load data");
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);

    if (isLoading) return <LoadingSkeleton variant="card" rows={3} />;
    if (error) return <div className="p-4 text-red-600 bg-red-50 rounded-lg">{error}</div>;

    if (indicators.length === 0) {
        return (
            <div className="p-8 text-center bg-gray-50 rounded-lg text-gray-500">
                No operational indicators available for your company yet.
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Health Score Overview */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white shadow-lg">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold mb-1">Operational Health Score</h2>
                        <p className="text-blue-100 opacity-90">Overall performance across all metrics</p>
                    </div>
                    <div className="text-center">
                        <div className="text-5xl font-bold">{overallHealth}</div>
                        <div className="text-sm text-blue-200 mt-1">/ 100</div>
                    </div>
                </div>
            </div>

            {/* Indicators Grid */}
            <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Key Performance Indicators</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {indicators.map((indicator) => (
                        <OperationalIndicatorCard
                            key={indicator.operational_indicator_code}
                            indicator={indicator}
                        />
                    ))}
                </div>
            </div>

            {/* Industry/Company Breakdown (Below Overview) */}
            <IndustryBreakdown indicators={indicators} />
        </div>
    );
}
