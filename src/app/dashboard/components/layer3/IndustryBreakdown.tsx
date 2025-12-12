import React from 'react';
import { OperationalIndicatorCard } from './OperationalIndicatorCard';

interface OperationalIndicator {
    indicator_id: string;
    indicator_name: string;
    current_value: number;
    baseline_value?: number;
    trend?: string;
    is_above_threshold?: boolean;
    impact_score?: number;
    category?: string;
    company_id?: string;
}

interface Props {
    indicators: OperationalIndicator[];
}

export function IndustryBreakdown({ indicators }: Props) {
    // Determine unique industries from indicators (assuming indicators might have industry metadata in future)
    // For now, indicators are fetched PER user/company. 
    // If the user is Admin, the API returns indicators for ALL companies (or we need to filter/group).

    // NOTE: The current API response structure `OperationalIndicator` is centered around a specific company.
    // If Admin fetches, we receive a list of indicators which contain `company_id`.

    const indicatorsByCompany = React.useMemo(() => {
        return indicators.reduce((acc, ind) => {
            const companyId = ind.company_id || 'Unknown';
            if (!acc[companyId]) acc[companyId] = [];
            acc[companyId].push(ind);
            return acc;
        }, {} as Record<string, OperationalIndicator[]>);
    }, [indicators]);

    if (Object.keys(indicatorsByCompany).length === 0) {
        return null;
    }

    return (
        <div className="space-y-8 mt-8 border-t border-gray-200 pt-8">
            <h3 className="text-xl font-bold text-gray-900">Industry / Company Breakdown</h3>

            {Object.entries(indicatorsByCompany).map(([companyId, companyIndicators]) => (
                <div key={companyId} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-50 rounded-lg">
                                <span className="text-xl">🏢</span>
                            </div>
                            <div>
                                <h4 className="font-semibold text-gray-900">{companyId}</h4>
                                <span className="text-xs text-gray-500">{companyIndicators.length} metrics</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {companyIndicators.map((indicator) => (
                            <OperationalIndicatorCard
                                key={`${indicator.company_id}-${indicator.indicator_id}`}
                                indicator={indicator}
                            />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
