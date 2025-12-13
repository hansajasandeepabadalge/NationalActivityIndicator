'use client';

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useNationalIndicators } from '@/hooks/useDashboard';
import { usePolling } from '@/hooks/usePolling';
import { LoadingSkeleton } from '@/app/dashboard/components/shared/LoadingSkeleton';
import { dashboardService } from '@/lib/api/dashboard';

type SortOption = 'value' | 'confidence' | 'change' | 'impact';

interface TopIndicatorsBarChartProps {
  limit?: number;
  height?: number;
  pollingInterval?: number;
}

const PESTEL_COLORS: Record<string, string> = {
  Political: '#6366f1',    // indigo-500
  Economic: '#10b981',     // emerald-500
  Social: '#a855f7',       // purple-500
  Technological: '#3b82f6', // blue-500
  Environmental: '#14b8a6', // teal-500
  Legal: '#f97316',        // orange-500
  Other: '#6b7280',        // gray-500
};

export function TopIndicatorsBarChart({
  limit = 10,
  height = 400,
  pollingInterval = 60000
}: TopIndicatorsBarChartProps) {
  const [sortBy, setSortBy] = useState<SortOption>('impact');

  const fetchFn = async () => {
    return await dashboardService.getNationalIndicators(undefined, limit, sortBy);
  };

  const { data, isLoading, error } = usePolling(fetchFn, {
    interval: pollingInterval,
    enabled: true
  });

  const sortButtons: Array<{ key: SortOption; label: string }> = [
    { key: 'impact', label: 'Impact' },
    { key: 'value', label: 'Value' },
    { key: 'confidence', label: 'Confidence' },
    { key: 'change', label: 'Change %' }
  ];

  if (isLoading && !data) {
    return <LoadingSkeleton variant="chart" />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
        <p className="text-red-600">Error loading indicators: {error.message}</p>
      </div>
    );
  }

  if (!data || data.indicators.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">No indicator data available</p>
      </div>
    );
  }

  // Transform data for the chart
  const chartData = data.indicators.slice(0, limit).map(ind => ({
    name: ind.indicator_name.length > 30
      ? ind.indicator_name.substring(0, 30) + '...'
      : ind.indicator_name,
    fullName: ind.indicator_name,
    value: ind.current_value || 0,
    confidence: (ind.confidence || 0) * 100,
    change: Math.abs(ind.change_percentage || 0),
    impact: ind.extra_metadata?.impact_score || 0,
    category: ind.pestel_category,
    color: PESTEL_COLORS[ind.pestel_category] || PESTEL_COLORS.Other
  }));

  // Determine which value to display based on sort
  const getDisplayValue = (item: typeof chartData[0]) => {
    switch (sortBy) {
      case 'value':
        return item.value;
      case 'confidence':
        return item.confidence;
      case 'change':
        return item.change;
      case 'impact':
      default:
        return item.impact;
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{data.fullName}</p>
          <div className="space-y-1 text-sm">
            <p className="text-gray-600">
              <span className="font-medium">Category:</span> {data.category}
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Value:</span> {data.value.toFixed(2)}
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Confidence:</span> {data.confidence.toFixed(1)}%
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Change:</span> {data.change.toFixed(1)}%
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Sort Buttons */}
      <div className="flex flex-wrap gap-2">
        {sortButtons.map(button => (
          <button
            key={button.key}
            onClick={() => setSortBy(button.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              sortBy === button.key
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Sort by {button.label}
          </button>
        ))}
      </div>

      {/* Bar Chart */}
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
          >
            <XAxis type="number" />
            <YAxis
              type="category"
              dataKey="name"
              width={140}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey={sortBy}
              radius={[0, 4, 4, 0]}
              onClick={(data) => console.log('Clicked:', data.fullName)}
              className="cursor-pointer"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  opacity={0.6 + (entry.confidence / 200)} // Gradient based on confidence
                  className="hover:opacity-100 transition-opacity"
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 justify-center text-xs">
        {Object.entries(PESTEL_COLORS).map(([category, color]) => (
          <div key={category} className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: color }}
            />
            <span className="text-gray-600">{category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
