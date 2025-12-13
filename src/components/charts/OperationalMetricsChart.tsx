'use client';

import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { OperationalIndicator } from '@/lib/api/types';

interface OperationalMetricsChartProps {
  indicators: OperationalIndicator[];
  height?: number;
}

export function OperationalMetricsChart({ indicators, height = 400 }: OperationalMetricsChartProps) {
  // For this chart, we'll show current vs baseline values for each indicator
  const chartData = useMemo(() => {
    if (!indicators || indicators.length === 0) return [];

    return indicators.map((indicator, index) => ({
      name: indicator.indicator_name.length > 20
        ? indicator.indicator_name.substring(0, 20) + '...'
        : indicator.indicator_name,
      fullName: indicator.indicator_name,
      current: indicator.current_value || 0,
      baseline: indicator.baseline_value || 0,
      deviation: indicator.deviation || 0,
      impact: indicator.impact_score || 0,
    }));
  }, [indicators]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white/95 backdrop-blur-md p-4 border-2 border-gray-200 rounded-xl shadow-2xl">
          <p className="font-bold text-gray-900 mb-3">{data.fullName}</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-gradient-to-br from-blue-500 to-blue-600"></div>
                <span className="text-sm text-gray-600">Current:</span>
              </div>
              <span className="font-bold text-blue-600">{data.current.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                <span className="text-sm text-gray-600">Baseline:</span>
              </div>
              <span className="font-semibold text-gray-600">{data.baseline.toFixed(2)}</span>
            </div>
            {data.deviation !== 0 && (
              <div className="pt-2 border-t border-gray-200">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs text-gray-500">Deviation:</span>
                  <span className={`font-bold text-sm ${data.deviation > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {data.deviation > 0 ? '+' : ''}{data.deviation.toFixed(2)}
                  </span>
                </div>
              </div>
            )}
            {data.impact !== 0 && (
              <div className="flex items-center justify-between gap-4">
                <span className="text-xs text-gray-500">Impact:</span>
                <span className="font-semibold text-purple-600 text-sm">{data.impact.toFixed(2)}</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = () => (
    <div className="flex items-center justify-center gap-6 mt-4">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded bg-gradient-to-br from-blue-500 to-blue-600 shadow-md"></div>
        <span className="text-sm font-medium text-gray-700">Current Value</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded bg-gray-400 shadow-md"></div>
        <span className="text-sm font-medium text-gray-700">Baseline</span>
      </div>
    </div>
  );

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No operational metrics data available</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 20, bottom: 60 }}
        >
          <defs>
            {/* Glassmorphism gradient for Current Value - Blue */}
            <linearGradient id="colorCurrent" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
              <stop offset="50%" stopColor="#3b82f6" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.1} />
            </linearGradient>

            {/* Glassmorphism gradient for Baseline - Gray */}
            <linearGradient id="colorBaseline" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#9ca3af" stopOpacity={0.6} />
              <stop offset="50%" stopColor="#9ca3af" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#9ca3af" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />

          <XAxis
            dataKey="name"
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

          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#3b82f6', strokeWidth: 1, strokeDasharray: '5 5' }} />

          <Legend content={<CustomLegend />} />

          {/* Baseline Area (behind) */}
          <Area
            type="monotone"
            dataKey="baseline"
            name="Baseline"
            stroke="#9ca3af"
            strokeWidth={2}
            strokeDasharray="5 5"
            fill="url(#colorBaseline)"
            fillOpacity={1}
            dot={{ r: 3, fill: '#9ca3af', strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 5, fill: '#9ca3af', strokeWidth: 2, stroke: '#fff' }}
          />

          {/* Current Value Area (in front) */}
          <Area
            type="monotone"
            dataKey="current"
            name="Current Value"
            stroke="#3b82f6"
            strokeWidth={3}
            fill="url(#colorCurrent)"
            fillOpacity={1}
            dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff', className: 'drop-shadow-lg' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
