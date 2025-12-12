import React from 'react';
import { OperationalIndicator } from '../../../services/operationalService';

interface Props {
    indicator: OperationalIndicator;
}

export function OperationalIndicatorCard({ indicator }: Props) {
    const {
        indicator_name,
        current_value,
        baseline_value,
        trend,
        is_above_threshold,
        impact_score,
        category
    } = indicator;

    // Status color mapping based on threshold and impact
    let statusLabel = 'healthy';
    let statusInfo = 'Normal';

    if (is_above_threshold) { // Logic: Above threshold usually means bad (e.g. high cost, delay) or depends on context, but schema implies 'requires attention'
        statusLabel = 'critical';
        statusInfo = 'Attention';
    } else if (impact_score > 0.5) {
        statusLabel = 'critical';
        statusInfo = 'Critical';
    } else if (impact_score > 0.2) {
        statusLabel = 'attention_needed';
        statusInfo = 'Warning';
    }

    const statusColors: Record<string, string> = {
        healthy: 'bg-green-100 text-green-800 border-green-200',
        attention_needed: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        critical: 'bg-red-100 text-red-800 border-red-200'
    };

    const statusColor = statusColors[statusLabel] || statusColors.healthy;

    // Trend icon mapping
    const TrendIcon = () => {
        if (trend === 'up') return <span className="text-red-500">↑</span>; // Assuming Up is bad usually for operational costs/delays, but could be good for productivity. 
        // Logic: The API TrendDirection.UP logic. 
        // Let's assume neutral for now or rely on specific indicator knowledge? 
        // Actually, schema just gives 'up'/'down'. 
        // Let's use generic arrows.
        if (trend === 'up') return <span className="text-gray-600">↑</span>;
        if (trend === 'down') return <span className="text-gray-600">↓</span>;
        return <span className="text-gray-400">→</span>;
    };

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
                <div>
                    <h4 className="font-semibold text-gray-800 text-sm uppercase tracking-wide">
                        {indicator_name}
                    </h4>
                    <span className="text-xs text-gray-500 block truncate max-w-[150px]">{category}</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${statusColor}`}>
                    {statusInfo}
                </span>
            </div>

            <div className="flex items-baseline gap-2 mb-3">
                <span className="text-3xl font-bold text-gray-900">
                    {Math.round(current_value)}
                </span>
                {/* Assuming scale is usually relevant to base 100 or just value. Removing /100 fixed text unless valid */}

                <span className="ml-auto text-sm font-medium flex items-center gap-1">
                    <TrendIcon />
                    <span className="text-gray-500 capitalize">{trend}</span>
                </span>
            </div>

            <div className="space-y-2 mt-4 pt-3 border-t border-gray-100">
                <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Industry Avg:</span>
                    <span className="font-medium text-gray-700">{Math.round(baseline_value)}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Impact Score:</span>
                    <span className="font-medium text-gray-700">{impact_score.toFixed(2)}</span>
                </div>
            </div>
        </div>
    );
}
