'use client';

import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { PestelDistribution } from '@/lib/api/types';

interface PestelDonutChartProps {
  data: Record<string, number>;
  onCategoryClick?: (category: string) => void;
  height?: number;
}

// PESTEL color mapping
const PESTEL_COLORS: Record<string, string> = {
  Political: '#6366f1',    // indigo-500
  Economic: '#10b981',     // emerald-500
  Social: '#a855f7',       // purple-500
  Technological: '#3b82f6', // blue-500
  Environmental: '#14b8a6', // teal-500
  Legal: '#f97316',        // orange-500
  Other: '#6b7280',        // gray-500
};

export function PestelDonutChart({ data, onCategoryClick, height = 300 }: PestelDonutChartProps) {
  // Transform data for Recharts
  const chartData = useMemo<PestelDistribution[]>(() => {
    return Object.entries(data).map(([category, count]) => ({
      category,
      count,
      color: PESTEL_COLORS[category] || PESTEL_COLORS.Other,
    }));
  }, [data]);

  const total = useMemo(() => {
    return chartData.reduce((sum, item) => sum + item.count, 0);
  }, [chartData]);

  // Custom label for center
  const renderCenterLabel = () => {
    return (
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dominantBaseline="middle"
        className="fill-gray-900 font-bold text-3xl"
      >
        {total}
      </text>
    );
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as PestelDistribution;
      const percentage = total > 0 ? ((data.count / total) * 100).toFixed(1) : '0';

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.category}</p>
          <p className="text-sm text-gray-600">
            {data.count} indicators ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom legend
  const renderLegend = (props: any) => {
    const { payload } = props;

    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry: any, index: number) => {
          const data = entry.payload as PestelDistribution;
          return (
            <button
              key={`legend-${index}`}
              onClick={() => onCategoryClick?.(data.category)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md hover:bg-gray-100 transition cursor-pointer"
            >
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: data.color }}
              />
              <span className="text-sm font-medium text-gray-700">
                {data.category}
              </span>
              <span className="text-sm text-gray-500">
                ({data.count})
              </span>
            </button>
          );
        })}
      </div>
    );
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            innerRadius="60%"
            outerRadius="80%"
            paddingAngle={2}
            dataKey="count"
            onClick={(data: PestelDistribution) => onCategoryClick?.(data.category)}
            className="cursor-pointer focus:outline-none"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
                className="hover:opacity-80 transition-opacity"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={renderLegend} />
          {renderCenterLabel()}
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
