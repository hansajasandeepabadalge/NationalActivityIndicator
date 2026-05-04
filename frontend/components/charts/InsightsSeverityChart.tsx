'use client';

import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend, Cell, CartesianGrid } from 'recharts';
import type { BusinessInsightList } from '@/lib/api/types';

interface InsightsSeverityChartProps {
  insightsData: BusinessInsightList | null;
  height?: number;
}

const SEVERITY_COLORS: Record<string, { risks: string; opportunities: string }> = {
  critical: { risks: '#dc2626', opportunities: '#10b981' },
  high: { risks: '#f97316', opportunities: '#22c55e' },
  medium: { risks: '#eab308', opportunities: '#84cc16' },
  low: { risks: '#f59e0b', opportunities: '#4ade80' },
};

const SEVERITY_ORDER = ['critical', 'high', 'medium', 'low'];

export function InsightsSeverityChart({ insightsData, height = 300 }: InsightsSeverityChartProps) {
  const chartData = useMemo(() => {
    if (!insightsData?.insights) return [];

    // Count insights by severity and type
    const severityCount: Record<string, { risks: number; opportunities: number }> = {
      critical: { risks: 0, opportunities: 0 },
      high: { risks: 0, opportunities: 0 },
      medium: { risks: 0, opportunities: 0 },
      low: { risks: 0, opportunities: 0 },
    };

    insightsData.insights.forEach((insight) => {
      const severity = insight.severity_level || 'medium';
      if (insight.insight_type === 'risk') {
        severityCount[severity].risks += 1;
      } else if (insight.insight_type === 'opportunity') {
        severityCount[severity].opportunities += 1;
      }
    });

    return SEVERITY_ORDER.map((severity) => ({
      severity: severity.charAt(0).toUpperCase() + severity.slice(1),
      risks: severityCount[severity].risks,
      opportunities: severityCount[severity].opportunities,
      riskColor: SEVERITY_COLORS[severity].risks,
      oppColor: SEVERITY_COLORS[severity].opportunities,
    }));
  }, [insightsData]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white/95 backdrop-blur-md p-4 border-2 border-gray-200 rounded-xl shadow-2xl">
          <p className="font-bold text-gray-900 mb-3 text-sm">{data.severity} Severity</p>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-red-500 to-red-600"></div>
              <span className="text-sm text-gray-600">Risks:</span>
              <span className="font-bold text-red-600 ml-auto">{data.risks}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-green-500 to-green-600"></div>
              <span className="text-sm text-gray-600">Opportunities:</span>
              <span className="font-bold text-green-600 ml-auto">{data.opportunities}</span>
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Total: <span className="font-semibold text-gray-700">{data.risks + data.opportunities}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = () => (
    <div className="flex items-center justify-center gap-6 mt-4">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded bg-gradient-to-br from-red-500 to-red-600 shadow-md"></div>
        <span className="text-sm font-medium text-gray-700">Risks</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded bg-gradient-to-br from-green-500 to-green-600 shadow-md"></div>
        <span className="text-sm font-medium text-gray-700">Opportunities</span>
      </div>
    </div>
  );

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
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="gradientRisks" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#dc2626" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#dc2626" stopOpacity={0.6} />
            </linearGradient>
            <linearGradient id="gradientOpportunities" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.6} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
          <XAxis
            dataKey="severity"
            tick={{ fontSize: 12, fill: '#6b7280', fontWeight: 500 }}
            stroke="#d1d5db"
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
            stroke="#d1d5db"
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }} />
          <Legend content={<CustomLegend />} />
          <Bar
            dataKey="risks"
            name="Risks"
            fill="url(#gradientRisks)"
            radius={[8, 8, 0, 0]}
            className="drop-shadow-md hover:opacity-80 transition-opacity"
          />
          <Bar
            dataKey="opportunities"
            name="Opportunities"
            fill="url(#gradientOpportunities)"
            radius={[8, 8, 0, 0]}
            className="drop-shadow-md hover:opacity-80 transition-opacity"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
