'use client';

import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { BusinessInsightList } from '@/lib/api/types';

interface RiskOpportunityPieChartProps {
  insightsData: BusinessInsightList | null;
  height?: number;
}

const CHART_COLORS = {
  risk: '#dc2626',         // red-600
  opportunity: '#10b981',  // green-500
  recommendation: '#3b82f6' // blue-500
};

export function RiskOpportunityPieChart({ insightsData, height = 300 }: RiskOpportunityPieChartProps) {
  const chartData = useMemo(() => {
    if (!insightsData?.insights) return [];

    const typeCounts = {
      risk: 0,
      opportunity: 0,
      recommendation: 0,
    };

    insightsData.insights.forEach((insight) => {
      const type = insight.insight_type;
      if (type in typeCounts) {
        typeCounts[type] += 1;
      }
    });

    return [
      { name: 'Risks', value: typeCounts.risk, color: CHART_COLORS.risk },
      { name: 'Opportunities', value: typeCounts.opportunity, color: CHART_COLORS.opportunity },
      { name: 'Recommendations', value: typeCounts.recommendation, color: CHART_COLORS.recommendation },
    ].filter(item => item.value > 0); // Only show non-zero values
  }, [insightsData]);

  const total = useMemo(() => {
    return chartData.reduce((sum, item) => sum + item.value, 0);
  }, [chartData]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : '0';

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            {data.value} insights ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

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

  const renderLegend = (props: any) => {
    const { payload } = props;

    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry: any, index: number) => {
          const data = entry.payload;
          return (
            <div
              key={`legend-${index}`}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md"
            >
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: data.color }}
              />
              <span className="text-sm font-medium text-gray-700">
                {data.name}
              </span>
              <span className="text-sm text-gray-500">
                ({data.value})
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No insights data available</p>
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
            dataKey="value"
            className="focus:outline-none"
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
