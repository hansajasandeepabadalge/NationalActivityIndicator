/**
 * Enhanced Operational Indicator Card with Sparkline
 */
import React from 'react';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { SparklineChart } from '@/components/charts/SparklineChart';
import { useIndicatorHistory } from '@/hooks/useIndicatorHistory';

interface OperationalIndicator {
    indicator_id: string;
    indicator_name: string;
    category: string;
    current_value: number;
    baseline_value?: number;
    deviation?: number;
    impact_score?: number;
    trend?: string;
    is_above_threshold?: boolean;
    is_below_threshold?: boolean;
}

interface IndicatorCardProps {
    indicator: OperationalIndicator;
    onClick?: () => void;
}

export const IndicatorCard: React.FC<IndicatorCardProps> = ({ indicator, onClick }) => {
    // Fetch 7-day history for sparkline
    const { data: historyData, isLoading } = useIndicatorHistory(indicator.indicator_id, 7);

    // Determine trend icon and color
    const getTrendIcon = () => {
        const trend = historyData?.trend_summary?.trend || indicator.trend || 'stable';
        switch (trend) {
            case 'increasing':
                return <TrendingUp className="w-4 h-4 text-green-500" />;
            case 'decreasing':
                return <TrendingDown className="w-4 h-4 text-red-500" />;
            default:
                return <Minus className="w-4 h-4 text-gray-500" />;
        }
    };

    const getTrendColor = () => {
        const trend = historyData?.trend_summary?.trend || indicator.trend || 'stable';
        switch (trend) {
            case 'increasing':
                return 'text-green-600';
            case 'decreasing':
                return 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    const getChangeText = () => {
        if (historyData?.trend_summary) {
            const change = historyData.trend_summary.change_percent;
            const sign = change > 0 ? '+' : '';
            return `${sign}${change.toFixed(1)}%`;
        }
        return indicator.deviation ? `${indicator.deviation > 0 ? '+' : ''}${indicator.deviation.toFixed(1)}` : '—';
    };

    // Prepare sparkline data
    const sparklineData = historyData?.history
        ? historyData.history.map(point => ({
            timestamp: point.timestamp,
            value: point.value
        }))
        : [];

    return (
        <div
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={onClick}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <Activity className="w-4 h-4 text-blue-500" />
                        <h4 className="text-sm font-semibold text-gray-900 truncate">
                            {indicator.indicator_name}
                        </h4>
                    </div>
                    <span className="text-xs text-gray-500">{indicator.category}</span>
                </div>
                {getTrendIcon()}
            </div>

            {/* Current Value */}
            <div className="mb-3">
                <div className="text-2xl font-bold text-gray-900">
                    {indicator.current_value?.toFixed(1) || '—'}
                </div>
                <div className={`text-sm font-medium ${getTrendColor()}`}>
                    {getChangeText()} <span className="text-xs text-gray-500">vs baseline</span>
                </div>
            </div>

            {/* Sparkline Chart */}
            <div className="mb-2">
                {isLoading ? (
                    <div className="h-10 bg-gray-100 rounded animate-pulse" />
                ) : sparklineData.length > 0 ? (
                    <div>
                        <div className="text-xs text-gray-500 mb-1">Last 7 Days</div>
                        <SparklineChart
                            data={sparklineData}
                            trend={historyData?.trend_summary?.trend}
                            height={40}
                        />
                    </div>
                ) : (
                    <div className="h-10 flex items-center justify-center text-xs text-gray-400">
                        No historical data
                    </div>
                )}
            </div>

            {/* Impact Score */}
            {indicator.impact_score && (
                <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Impact Score</span>
                    <span className="font-semibold text-gray-900">
                        {indicator.impact_score.toFixed(1)}/10
                    </span>
                </div>
            )}
        </div>
    );
};

export default IndicatorCard;
