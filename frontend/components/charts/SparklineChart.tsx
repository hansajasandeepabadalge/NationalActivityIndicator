/**
 * Sparkline Chart Component
 * 
 * Lightweight inline chart showing trend over time.
 * Modern design with gradient fill and mirror effect.
 */
import React from 'react';
import { AreaChart, Area, ResponsiveContainer, YAxis } from 'recharts';

interface SparklineChartProps {
    data: Array<{ timestamp: string; value: number }>;
    trend?: 'increasing' | 'decreasing' | 'stable';
    width?: string | number;
    height?: number;
    className?: string;
}

export const SparklineChart: React.FC<SparklineChartProps> = ({
    data,
    trend = 'stable',
    width = '100%',
    height = 40,
    className = ''
}) => {
    // Determine colors based on trend
    const getColors = () => {
        switch (trend) {
            case 'increasing':
                return {
                    stroke: '#10b981', // green-500
                    fill: 'url(#colorGreen)',
                    gradientStart: '#10b98180', // green-500 with 50% opacity
                    gradientEnd: '#10b98110'    // green-500 with 6% opacity
                };
            case 'decreasing':
                return {
                    stroke: '#ef4444', // red-500
                    fill: 'url(#colorRed)',
                    gradientStart: '#ef444480',
                    gradientEnd: '#ef444410'
                };
            default:
                return {
                    stroke: '#6b7280', // gray-500
                    fill: 'url(#colorGray)',
                    gradientStart: '#6b728080',
                    gradientEnd: '#6b728010'
                };
        }
    };

    const colors = getColors();

    // If no data, show empty state
    if (!data || data.length === 0) {
        return (
            <div
                className={`flex items-center justify-center ${className}`}
                style={{ width, height }}
            >
                <span className="text-xs text-gray-400">No data</span>
            </div>
        );
    }

    // Sort data by timestamp
    const sortedData = [...data].sort((a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Calculate domain for better visualization
    const values = sortedData.map(d => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const padding = (maxValue - minValue) * 0.15 || 1;

    return (
        <div className={`relative overflow-hidden rounded-lg ${className}`} style={{ width, height }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sortedData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
                    <defs>
                        <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.5} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                        </linearGradient>
                        <linearGradient id="colorRed" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} />
                        </linearGradient>
                        <linearGradient id="colorGray" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6b7280" stopOpacity={0.5} />
                            <stop offset="95%" stopColor="#6b7280" stopOpacity={0.05} />
                        </linearGradient>
                    </defs>
                    <YAxis
                        domain={[minValue - padding, maxValue + padding]}
                        hide
                    />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={colors.stroke}
                        strokeWidth={2}
                        fill={colors.fill}
                        fillOpacity={1}
                        isAnimationActive={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default SparklineChart;
