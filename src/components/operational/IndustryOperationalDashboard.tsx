'use client';

/**
 * Industry-Wise Operational Indicators Dashboard
 * Comprehensive view of operational metrics across 6 industries
 */

import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line } from 'recharts';
import {
    IndustryType,
    INDUSTRY_COLORS,
    INDUSTRY_ICONS,
    MOCK_INDUSTRY_INDICATORS,
    MOCK_INDUSTRY_PERFORMANCE,
    getIndicatorsByIndustry,
    getTopIndicators,
    getIndustryPerformance,
    IndustryIndicator,
} from '@/types/industryIndicators';

export function IndustryOperationalDashboard() {
    const [selectedIndustry, setSelectedIndustry] = useState<IndustryType | 'All'>('All');
    const [selectedMetric, setSelectedMetric] = useState<string>('Production Efficiency');

    const industries: Array<IndustryType | 'All'> = ['All', 'Manufacturing', 'Technology', 'Finance', 'Healthcare', 'Retail', 'Agriculture'];

    // Get filtered indicators
    const filteredIndicators = useMemo(() => {
        return getIndicatorsByIndustry(selectedIndustry);
    }, [selectedIndustry]);

    // Get top indicators
    const topIndicators = useMemo(() => {
        return getTopIndicators(10);
    }, []);

    // Get industry-specific indicators for selected industry
    const industrySpecificIndicators = useMemo(() => {
        if (selectedIndustry === 'All') return [];
        return getIndicatorsByIndustry(selectedIndustry);
    }, [selectedIndustry]);

    // Prepare comparison data for selected metric
    const comparisonData = useMemo(() => {
        const metricsByIndustry = MOCK_INDUSTRY_INDICATORS.filter(ind =>
            ind.indicator_name.toLowerCase().includes(selectedMetric.toLowerCase().split(' ')[0])
        );

        return industries.filter(ind => ind !== 'All').map(industry => {
            const indicator = metricsByIndustry.find(ind => ind.industry === industry);
            return {
                industry,
                value: indicator?.current_value || 0,
                baseline: indicator?.baseline_value || 0,
            };
        });
    }, [selectedMetric]);

    // Prepare radar chart data
    const radarData = useMemo(() => {
        if (selectedIndustry === 'All') return [];

        const performance = getIndustryPerformance(selectedIndustry as IndustryType);
        if (!performance) return [];

        return Object.entries(performance.dimensions).map(([key, value]) => ({
            dimension: key.charAt(0).toUpperCase() + key.slice(1),
            value,
            baseline: 75, // Industry average baseline
        }));
    }, [selectedIndustry]);

    const getTrendIcon = (trend: string) => {
        if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />;
        if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-600" />;
        return <Minus className="w-4 h-4 text-gray-600" />;
    };

    const getStatusColor = (status: string) => {
        if (status === 'good') return 'bg-green-100 text-green-800 border-green-200';
        if (status === 'warning') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        return 'bg-red-100 text-red-800 border-red-200';
    };

    return (
        <div className="space-y-6">
            {/* Industry Selector */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Select Industry</h3>
                        <p className="text-sm text-gray-500">Filter operational indicators by industry sector</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <select
                            value={selectedIndustry}
                            onChange={(e) => setSelectedIndustry(e.target.value as IndustryType | 'All')}
                            className="px-4 py-2 border-2 border-gray-300 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            {industries.map((industry) => (
                                <option key={industry} value={industry}>
                                    {INDUSTRY_ICONS[industry as IndustryType] || '📊'} {industry}
                                </option>
                            ))}
                        </select>
                        {selectedIndustry !== 'All' && (
                            <div
                                className="px-4 py-2 rounded-lg font-semibold text-white"
                                style={{ backgroundColor: INDUSTRY_COLORS[selectedIndustry as IndustryType] }}
                            >
                                {INDUSTRY_ICONS[selectedIndustry as IndustryType]} {selectedIndustry}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Dashboard Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top Indicators */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Top Performing Indicators
                    </h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {topIndicators.slice(0, 8).map((indicator, index) => (
                            <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                                <div className="flex items-center justify-between mb-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">{INDUSTRY_ICONS[indicator.industry]}</span>
                                        <span className="text-sm font-medium text-gray-900">{indicator.indicator_name}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {getTrendIcon(indicator.trend)}
                                        <span className={`text-sm font-bold ${indicator.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {indicator.change_percentage > 0 ? '+' : ''}{indicator.change_percentage.toFixed(1)}%
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between text-xs text-gray-500">
                                    <span>{indicator.industry}</span>
                                    <span className="font-semibold text-gray-900">{indicator.current_value.toFixed(1)} {indicator.unit}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Industry Comparison Chart */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <div className="mb-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Industry Comparison</h3>
                        <select
                            value={selectedMetric}
                            onChange={(e) => setSelectedMetric(e.target.value)}
                            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option>Production Efficiency</option>
                            <option>Quality Score</option>
                            <option>Growth Rate</option>
                            <option>Innovation Index</option>
                            <option>Customer Satisfaction</option>
                        </select>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={comparisonData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis
                                dataKey="industry"
                                tick={{ fontSize: 11, fill: '#6b7280' }}
                                angle={-45}
                                textAnchor="end"
                                height={80}
                            />
                            <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '2px solid #e5e7eb' }}
                            />
                            <Bar dataKey="value" name="Current" radius={[8, 8, 0, 0]}>
                                {comparisonData.map((entry, index) => (
                                    <rect
                                        key={`cell-${index}`}
                                        fill={INDUSTRY_COLORS[entry.industry as IndustryType]}
                                        className="hover:opacity-80 transition-opacity"
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Industry-Specific Metrics (only when industry is selected) */}
            {selectedIndustry !== 'All' && industrySpecificIndicators.length > 0 && (
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        {INDUSTRY_ICONS[selectedIndustry as IndustryType]} {selectedIndustry} Key Metrics
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {industrySpecificIndicators.map((indicator, index) => (
                            <div key={index} className={`p-4 rounded-xl border-2 ${getStatusColor(indicator.status)}`}>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs font-medium uppercase tracking-wide">{indicator.category}</span>
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getStatusColor(indicator.status)}`}>
                                        {indicator.status}
                                    </span>
                                </div>
                                <h4 className="text-sm font-semibold text-gray-900 mb-2">{indicator.indicator_name}</h4>
                                <div className="flex items-baseline gap-2 mb-2">
                                    <span className="text-2xl font-bold text-gray-900">{indicator.current_value.toFixed(1)}</span>
                                    <span className="text-sm text-gray-600">{indicator.unit}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {indicator.change_percentage >= 0 ? (
                                        <ArrowUp className="w-4 h-4 text-green-600" />
                                    ) : (
                                        <ArrowDown className="w-4 h-4 text-red-600" />
                                    )}
                                    <span className={`text-sm font-semibold ${indicator.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {indicator.change_percentage > 0 ? '+' : ''}{indicator.change_percentage.toFixed(1)}%
                                    </span>
                                    <span className="text-xs text-gray-500">vs baseline</span>
                                </div>
                                {/* Mini sparkline */}
                                {indicator.sparkline_data && (
                                    <div className="mt-3 h-8">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={indicator.sparkline_data.map((val, i) => ({ value: val }))}>
                                                <Line
                                                    type="monotone"
                                                    dataKey="value"
                                                    stroke={INDUSTRY_COLORS[indicator.industry]}
                                                    strokeWidth={2}
                                                    dot={false}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Bottom Row: Radar Chart & Trend Analysis */}
            {selectedIndustry !== 'All' && radarData.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Performance Radar */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            {selectedIndustry} Performance Dimensions
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart data={radarData}>
                                <PolarGrid stroke="#e5e7eb" />
                                <PolarAngleAxis
                                    dataKey="dimension"
                                    tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
                                />
                                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
                                <Radar
                                    name="Current"
                                    dataKey="value"
                                    stroke={INDUSTRY_COLORS[selectedIndustry as IndustryType]}
                                    fill={INDUSTRY_COLORS[selectedIndustry as IndustryType]}
                                    fillOpacity={0.6}
                                    strokeWidth={2}
                                />
                                <Radar
                                    name="Baseline"
                                    dataKey="baseline"
                                    stroke="#9ca3af"
                                    fill="#9ca3af"
                                    fillOpacity={0.2}
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '2px solid #e5e7eb' }}
                                />
                                <Legend />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Summary Stats */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            {selectedIndustry} Summary
                        </h3>
                        <div className="space-y-4">
                            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                                <div className="text-sm text-blue-600 font-medium mb-1">Total Indicators</div>
                                <div className="text-3xl font-bold text-blue-900">{industrySpecificIndicators.length}</div>
                            </div>
                            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                                <div className="text-sm text-green-600 font-medium mb-1">Performing Well</div>
                                <div className="text-3xl font-bold text-green-900">
                                    {industrySpecificIndicators.filter(ind => ind.status === 'good').length}
                                </div>
                            </div>
                            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                                <div className="text-sm text-yellow-600 font-medium mb-1">Needs Attention</div>
                                <div className="text-3xl font-bold text-yellow-900">
                                    {industrySpecificIndicators.filter(ind => ind.status === 'warning').length}
                                </div>
                            </div>
                            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                                <div className="text-sm text-purple-600 font-medium mb-1">Average Growth</div>
                                <div className="text-3xl font-bold text-purple-900">
                                    {(industrySpecificIndicators.reduce((sum, ind) => sum + ind.change_percentage, 0) / industrySpecificIndicators.length).toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
