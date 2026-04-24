'use client';

/**
 * Company Profile Card
 * Displays comprehensive company information with stock data, impacts, and insights
 */

import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Lightbulb, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import {
    CompanyProfile,
    formatCurrency,
    formatPercent,
    getImpactColor,
    SECTOR_COLORS,
    SECTOR_ICONS,
} from '@/types/companyProfiles';

interface CompanyProfileCardProps {
    company: CompanyProfile;
    onClick?: () => void;
    compact?: boolean;
}

export function CompanyProfileCard({ company, onClick, compact = false }: CompanyProfileCardProps) {
    const { stock_data, sector, sensitivity_indicators, business_insights, recent_incidents_impact } = company;

    // Prepare price history data for chart
    const priceData = stock_data.price_history_30d.map((price, index) => ({
        day: index + 1,
        price,
    }));

    // Get price change color
    const getPriceChangeColor = (change: number) => {
        if (change > 0) return 'text-green-600';
        if (change < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    // Get trend icon
    const getTrendIcon = (change: number) => {
        if (change > 0) return <TrendingUp className="w-4 h-4" />;
        if (change < 0) return <TrendingDown className="w-4 h-4" />;
        return <Minus className="w-4 h-4" />;
    };

    if (compact) {
        return (
            <div
                onClick={onClick}
                className="bg-white rounded-xl shadow-lg border-2 border-gray-200 p-4 hover:border-blue-400 hover:shadow-xl transition-all cursor-pointer"
            >
                <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">{SECTOR_ICONS[sector]}</span>
                        <div>
                            <h3 className="font-bold text-gray-900">{company.ticker}</h3>
                            <p className="text-xs text-gray-500">{company.name}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">LKR {stock_data.current_price.toFixed(2)}</p>
                        <p className={`text-sm font-semibold flex items-center gap-1 justify-end ${getPriceChangeColor(stock_data.price_change_1d)}`}>
                            {getTrendIcon(stock_data.price_change_1d)}
                            {formatPercent(stock_data.price_change_1d)}
                        </p>
                    </div>
                </div>

                {/* Mini sparkline */}
                <div className="h-12 -mx-2">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={priceData}>
                            <Line
                                type="monotone"
                                dataKey="price"
                                stroke={SECTOR_COLORS[sector]}
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    return (
        <div
            onClick={onClick}
            className="bg-white rounded-xl shadow-xl border-2 border-gray-200 p-6 hover:border-blue-400 hover:shadow-2xl transition-all cursor-pointer"
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div>
                    <h2 className="text-xl font-bold text-gray-900">{company.name}</h2>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm font-semibold text-gray-600">{company.ticker}</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span
                            className="px-2 py-0.5 rounded-full text-xs font-semibold text-white"
                            style={{ backgroundColor: SECTOR_COLORS[sector] }}
                        >
                            {sector}
                        </span>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-500">Market Cap</p>
                    <p className="text-lg font-bold text-gray-900">{formatCurrency(company.market_cap)}</p>
                </div>
            </div>

            {/* Stock Performance */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                    <div>
                        <p className="text-sm text-gray-600 mb-1">Current Price</p>
                        <p className="text-3xl font-bold text-gray-900">LKR {stock_data.current_price.toFixed(2)}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-gray-600 mb-1">1D Change</p>
                        <p className={`text-2xl font-bold flex items-center gap-2 justify-end ${getPriceChangeColor(stock_data.price_change_1d)}`}>
                            {getTrendIcon(stock_data.price_change_1d)}
                            {formatPercent(stock_data.price_change_1d)}
                        </p>
                    </div>
                </div>

                {/* Price chart */}
                <div className="h-24 -mx-2">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={priceData}>
                            <Line
                                type="monotone"
                                dataKey="price"
                                stroke={SECTOR_COLORS[sector]}
                                strokeWidth={3}
                                dot={false}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '2px solid #e5e7eb' }}
                                formatter={(value: number) => [`LKR ${value.toFixed(2)}`, 'Price']}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Performance metrics */}
                <div className="grid grid-cols-4 gap-2 mt-3">
                    {[
                        { label: '1W', value: stock_data.price_change_1w },
                        { label: '1M', value: stock_data.price_change_1m },
                        { label: '3M', value: stock_data.price_change_3m },
                        { label: '1Y', value: stock_data.price_change_1y },
                    ].map((item, index) => (
                        <div key={index} className="text-center">
                            <p className="text-xs text-gray-500">{item.label}</p>
                            <p className={`text-sm font-bold ${getPriceChangeColor(item.value)}`}>
                                {formatPercent(item.value, 1)}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Sensitivity Indicators */}
            <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Most Sensitive To:</h3>
                <div className="space-y-2">
                    {sensitivity_indicators.slice(0, 3).map((indicator, index) => (
                        <div key={index} className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">{indicator.indicator_name}</span>
                            <div className="flex items-center gap-2">
                                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${indicator.correlation > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                        style={{ width: `${Math.abs(indicator.correlation) * 100}%` }}
                                    />
                                </div>
                                <span className={`text-sm font-semibold w-12 text-right ${indicator.correlation > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {(indicator.correlation * 100).toFixed(0)}%
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Incidents Impact */}
            {recent_incidents_impact.length > 0 && (
                <div className="mb-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Recent Incidents Impact:</h3>
                    <div className="space-y-2">
                        {recent_incidents_impact.slice(0, 2).map((incident, index) => (
                            <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium text-gray-900">{incident.incident_name}</span>
                                    <span className={`text-sm font-bold ${getImpactColor(incident.stock_impact_percent)}`}>
                                        {formatPercent(incident.stock_impact_percent)}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500">{incident.operational_impact}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Business Insights */}
            <div className="grid grid-cols-2 gap-3">
                {/* Risks */}
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-red-600" />
                        <span className="text-sm font-semibold text-red-900">Risks</span>
                    </div>
                    <p className="text-xs text-red-700">
                        {business_insights.risks.length} identified
                    </p>
                </div>

                {/* Opportunities */}
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 mb-2">
                        <Lightbulb className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-semibold text-green-900">Opportunities</span>
                    </div>
                    <p className="text-xs text-green-700">
                        {business_insights.opportunities.length} identified
                    </p>
                </div>
            </div>

            {/* View Details Button */}
            <button className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                View Full Profile →
            </button>
        </div>
    );
}
