'use client';

import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { BusinessInsightList } from '@/lib/api/types';

interface InsightsCategoryChartProps {
  insightsData: BusinessInsightList | null;
  height?: number;
}

// Modern gradient color palette for categories
const CATEGORY_COLORS: Record<string, { solid: string; gradient: string }> = {
  Political: { solid: '#6366f1', gradient: 'url(#gradientPolitical)' },
  Economic: { solid: '#10b981', gradient: 'url(#gradientEconomic)' },
  Social: { solid: '#a855f7', gradient: 'url(#gradientSocial)' },
  Technological: { solid: '#3b82f6', gradient: 'url(#gradientTechnological)' },
  Environmental: { solid: '#14b8a6', gradient: 'url(#gradientEnvironmental)' },
  Legal: { solid: '#f97316', gradient: 'url(#gradientLegal)' },
  Operational: { solid: '#8b5cf6', gradient: 'url(#gradientOperational)' },
  Strategic: { solid: '#ec4899', gradient: 'url(#gradientStrategic)' },
  Financial: { solid: '#10b981', gradient: 'url(#gradientFinancial)' },
  Market: { solid: '#f59e0b', gradient: 'url(#gradientMarket)' },
  Default: { solid: '#6b7280', gradient: 'url(#gradientDefault)' },
};

export function InsightsCategoryChart({ insightsData, height = 350 }: InsightsCategoryChartProps) {
  const chartData = useMemo(() => {
    if (!insightsData?.insights || !insightsData?.by_category) return [];

    return Object.entries(insightsData.by_category)
      .map(([category, count]) => ({
        category: category.charAt(0).toUpperCase() + category.slice(1),
        count,
        color: CATEGORY_COLORS[category]?.solid || CATEGORY_COLORS.Default.solid,
        gradient: CATEGORY_COLORS[category]?.gradient || CATEGORY_COLORS.Default.gradient,
      }))
      .sort((a, b) => b.count - a.count) // Sort by count descending
      .slice(0, 10); // Top 10 categories
  }, [insightsData]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const total = insightsData?.total || 0;
      const percentage = total > 0 ? ((data.count / total) * 100).toFixed(1) : '0';

      return (
        <div className="bg-white/95 backdrop-blur-md p-4 border-2 border-gray-200 rounded-xl shadow-2xl">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: data.color }}></div>
            <p className="font-bold text-gray-900">{data.category}</p>
          </div>
          <p className="text-sm text-gray-600">
            <span className="font-semibold text-gray-900">{data.count}</span> insights
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {percentage}% of total
          </p>
        </div>
      );
    }
    return null;
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No category data available</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <defs>
            {Object.entries(CATEGORY_COLORS).map(([key, value]) => (
              <linearGradient key={key} id={`gradient${key}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={value.solid} stopOpacity={0.9} />
                <stop offset="100%" stopColor={value.solid} stopOpacity={0.6} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
          <XAxis
            dataKey="category"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
            stroke="#d1d5db"
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
            stroke="#d1d5db"
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }} />
          <Bar dataKey="count" name="Insights Count" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.gradient}
                className="hover:opacity-80 transition-opacity cursor-pointer drop-shadow-md"
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
