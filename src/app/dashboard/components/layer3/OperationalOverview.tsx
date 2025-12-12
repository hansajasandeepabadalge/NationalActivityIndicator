import React, { useMemo } from 'react';
import { useOperationalIndicators } from '@/hooks/useDashboard';
import { operationalService } from '../../../services/operationalService';
import { OperationalIndicatorCard } from './OperationalIndicatorCard';
import { IndustryBreakdown } from './IndustryBreakdown';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

export function OperationalOverview({ selectedCompanyId }: { selectedCompanyId?: string }) {
    const { data: indicators, isLoading, error } = useOperationalIndicators(20);

    // Filter indicators
    const filteredIndicators = useMemo(() => {
        if (!indicators) return [];
        if (!selectedCompanyId) return indicators;
        return indicators.filter(ind => (ind as any).company_id === selectedCompanyId);
    }, [indicators, selectedCompanyId]);

    // Calculate Health Score
    const overallHealth = useMemo(() => {
        return operationalService.calculateOverallHealth(filteredIndicators);
    }, [filteredIndicators]);

    if (isLoading) return <LoadingSkeleton variant="card" rows={3} />;
    if (error) return <div className="p-4 text-red-600 bg-red-50 rounded-lg">{error}</div>;

    if (filteredIndicators.length === 0) {
        return (
            <div className="p-8 text-center bg-gray-50 rounded-lg text-gray-500">
                {selectedCompanyId ? "No operational indicators for this company." : "No operational indicators available."}
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
                        <p className="text-blue-100 opacity-90">
                            {selectedCompanyId ? "Company Performance" : "Overall Performance (All Companies)"}
                        </p>
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
                    {filteredIndicators.slice(0, 9).map((indicator) => (
                        <OperationalIndicatorCard
                            key={`${indicator.company_id}-${indicator.indicator_id}`}
                            indicator={indicator}
                        />
                    ))}
                </div>
            </div>

            {/* Industry/Company Breakdown (Below Overview) */}
            {/* Only show breakdown if NO specific company selected, OR if we want to show details even for single company */}
            <IndustryBreakdown indicators={filteredIndicators} />
        </div>
    );
}
