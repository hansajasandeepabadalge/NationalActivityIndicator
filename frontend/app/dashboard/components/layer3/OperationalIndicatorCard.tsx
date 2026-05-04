import React from 'react';
import { TrendingUp, TrendingDown, Minus, Activity, ChevronRight } from 'lucide-react';
import { OperationalIndicator } from '../../../services/operationalService';
import { SparklineChart } from '@/components/charts/SparklineChart';
import { useIndicatorHistory } from '@/hooks/useIndicatorHistory';

interface Props {
    indicator: OperationalIndicator;
}

export function OperationalIndicatorCard({ indicator }: Props) {
    const {
        indicator_id,
        indicator_name,
        current_value,
        baseline_value,
        trend,
        is_above_threshold,
        impact_score,
        category
    } = indicator;

    // Fetch 7-day history for sparkline
    const { data: historyData, isLoading: historyLoading } = useIndicatorHistory(indicator_id, 7);

    // Status color mapping based on threshold and impact
    let statusLabel = 'healthy';
    let statusInfo = 'Normal';

    if (is_above_threshold) {
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
        const trendValue = historyData?.trend_summary?.trend || trend;
        if (trendValue === 'increasing' || trendValue === 'up') {
            return <TrendingUp className="w-4 h-4 text-green-500" />;
        }
        if (trendValue === 'decreasing' || trendValue === 'down') {
            return <TrendingDown className="w-4 h-4 text-red-500" />;
        }
        return <Minus className="w-4 h-4 text-gray-400" />;
    };

    // Get change percentage
    const getChangeText = () => {
        if (historyData?.trend_summary) {
            const change = historyData.trend_summary.change_percent;
            const sign = change > 0 ? '+' : '';
            return `${sign}${change.toFixed(1)}%`;
        }
        return '—';
    };

    // Prepare sparkline data
    const sparklineData = historyData?.history
        ? historyData.history.map(point => ({
            timestamp: point.timestamp,
            value: point.value
        }))
        : [];

    return (
        <div className="relative bg-white rounded-lg border border-gray-200 p-3 shadow-sm hover:shadow-lg transition-all group cursor-pointer">
            <div className="flex justify-between items-start mb-2">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                        <Activity className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                        <h4 className="font-semibold text-gray-800 text-xs uppercase tracking-wide truncate">
                            {indicator_name}
                        </h4>
                    </div>
                    <span className="text-[10px] text-gray-500 block truncate">{category}</span>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                    <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-medium border ${statusColor} whitespace-nowrap`}>
                        {statusInfo}
                    </span>
                    <ChevronRight className="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-500 transition-colors" />
                </div>
            </div>

            <div className="flex items-baseline gap-2 mb-2">
                <span className="text-2xl font-bold text-gray-900">
                    {Math.round(current_value)}
                </span>

                <span className="ml-auto text-xs font-medium flex items-center gap-1">
                    <TrendIcon />
                    <span className="text-gray-600">{getChangeText()}</span>
                </span>
            </div>

            {/* Sparkline Chart */}
            <div className="mb-2 relative">
                {historyLoading ? (
                    <div className="h-10 bg-gray-100 rounded animate-pulse" />
                ) : sparklineData.length > 0 ? (
                    <div>
                        <div className="text-[10px] text-gray-500 mb-1 font-medium">Last 7 Days</div>
                        <div className="relative z-0">
                            <SparklineChart
                                data={sparklineData}
                                trend={historyData?.trend_summary?.trend}
                                height={40}
                            />
                        </div>
                    </div>
                ) : (
                    <div className="h-10 flex items-center justify-center text-[10px] text-gray-400 bg-gray-50 rounded">
                        No historical data
                    </div>
                )}
            </div>

            <div className="space-y-1 pt-2 border-t border-gray-100">
                <div className="flex justify-between text-[10px]">
                    <span className="text-gray-500">Baseline:</span>
                    <span className="font-medium text-gray-700">{Math.round(baseline_value)}</span>
                </div>
                <div className="flex justify-between text-[10px]">
                    <span className="text-gray-500">Impact:</span>
                    <span className="font-medium text-gray-700">{impact_score.toFixed(1)}/10</span>
                </div>
            </div>
        </div>
    );
}
