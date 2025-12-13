'use client';

import React, { useMemo } from 'react';
import { SparklineChart } from './SparklineChart';
import { useNationalIndicatorHistoryBatch } from '@/hooks/useIndicatorHistory';
import { LoadingSkeleton } from '@/app/dashboard/components/shared/LoadingSkeleton';
import type { NationalIndicator, IndicatorHistoryBatch } from '@/lib/api/types';

interface IndicatorTrendGridProps {
  indicators: NationalIndicator[];
  days?: number;
  pollingInterval?: number;
}

interface IndicatorCardData {
  indicator_id: string;
  indicator_name: string;
  category: string;
  current_value: number | null;
  change_percentage: number | null;
  trend: 'up' | 'down' | 'stable';
  history: Array<{ timestamp: string; value: number }>;
}

export function IndicatorTrendGrid({
  indicators,
  days = 30,
  pollingInterval = 30000
}: IndicatorTrendGridProps) {
  // Early return if no indicators
  if (!indicators || indicators.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <p className="text-gray-500 text-sm">No indicators available for visualization</p>
      </div>
    );
  }

  const indicatorIds = useMemo(
    () => indicators.map(ind => ind.indicator_id),
    [indicators]
  );

  const { data: historyData, isLoading, error } = useNationalIndicatorHistoryBatch({
    indicatorIds,
    days,
    enabled: indicatorIds.length > 0,
    pollingInterval
  });

  // Merge indicator data with history
  const cardData = useMemo<IndicatorCardData[]>(() => {
    if (!historyData) return [];

    return indicators.map(indicator => {
      const history = historyData[indicator.indicator_id]?.history || [];

      return {
        indicator_id: indicator.indicator_id,
        indicator_name: indicator.indicator_name,
        category: indicator.pestel_category,
        current_value: indicator.current_value,
        change_percentage: indicator.change_percentage,
        trend: indicator.trend,
        history: history.map(h => ({
          timestamp: h.timestamp,
          value: h.value
        }))
      };
    });
  }, [indicators, historyData]);

  if (isLoading && !historyData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <LoadingSkeleton key={i} variant="card" rows={2} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
        <p className="text-red-600 font-semibold mb-2">Error loading trend data</p>
        <p className="text-red-500 text-sm">{error?.message || JSON.stringify(error)}</p>
      </div>
    );
  }

  if (cardData.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">No indicator data available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cardData.map(indicator => (
        <IndicatorTrendCard key={indicator.indicator_id} indicator={indicator} />
      ))}
    </div>
  );
}

interface IndicatorTrendCardProps {
  indicator: IndicatorCardData;
}

function IndicatorTrendCard({ indicator }: IndicatorTrendCardProps) {
  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendLabel = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'increasing';
      case 'down':
        return 'decreasing';
      default:
        return 'stable';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate" title={indicator.indicator_name}>
            {indicator.indicator_name}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">{indicator.category}</p>
        </div>
      </div>

      {/* Value and Change */}
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-2xl font-bold text-gray-900">
          {indicator.current_value !== null ? indicator.current_value.toFixed(1) : 'N/A'}
        </span>
        {indicator.change_percentage !== null && (
          <span className={`text-sm font-medium ${getTrendColor(indicator.trend)}`}>
            {indicator.change_percentage >= 0 ? '+' : ''}
            {indicator.change_percentage.toFixed(1)}%
          </span>
        )}
      </div>

      {/* Sparkline */}
      <div className="h-12">
        <SparklineChart
          data={indicator.history}
          trend={getTrendLabel(indicator.trend) as 'increasing' | 'decreasing' | 'stable'}
          height={48}
        />
      </div>

      {/* Footer */}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
        <span>{indicator.history.length} data points</span>
        <span className="capitalize">{getTrendLabel(indicator.trend)}</span>
      </div>
    </div>
  );
}
