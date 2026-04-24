'use client';

/**
 * Enhanced Company Impact Card
 * Shows national indicator impacts with percentage bars and overall trend
 */

import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Lightbulb, CloudRain, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import {
    CompanyProfile,
    SECTOR_COLORS,
} from '@/types/companyProfiles';

interface CompanyImpactCardProps {
    company: CompanyProfile;
    onClick?: () => void;
}

export function CompanyImpactCard({ company, onClick }: CompanyImpactCardProps) {
    const { sector, sensitivity_indicators, business_insights, recent_incidents_impact } = company;

    // Calculate overall trend from recent incidents
    const overallImpact = recent_incidents_impact.reduce((sum, incident) => sum + incident.stock_impact_percent, 0);
    const avgImpact = recent_incidents_impact.length > 0 ? overallImpact / recent_incidents_impact.length : 0;

    // Get trend icon and color
    const getTrendDisplay = () => {
        if (avgImpact > 2) {
            return {
                icon: <TrendingUp className="w-6 h-6" />,
                color: 'text-green-600',
                bgColor: 'bg-green-50',
                borderColor: 'border-green-200',
                label: 'Growing',
                value: `+${avgImpact.toFixed(1)}%`
            };
        } else if (avgImpact < -2) {
            return {
                icon: <TrendingDown className="w-6 h-6" />,
                color: 'text-red-600',
                bgColor: 'bg-red-50',
                borderColor: 'border-red-200',
                label: 'Declining',
                value: `${avgImpact.toFixed(1)}%`
            };
        } else {
            return {
                icon: <Minus className="w-6 h-6" />,
                color: 'text-gray-600',
                bgColor: 'bg-gray-50',
                borderColor: 'border-gray-200',
                label: 'Stable',
                value: `${avgImpact.toFixed(1)}%`
            };
        }
    };

    const trend = getTrendDisplay();

    return (
        <div
            onClick={onClick}
            className="bg-white rounded-lg shadow-md border border-gray-200 p-5 hover:shadow-xl hover:border-blue-300 transition-all cursor-pointer"
        >
            {/* Header with Trend Badge */}
            <div className="mb-4">
                <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900">{company.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-gray-600">{company.ticker}</span>
                            <span className="text-xs text-gray-400">•</span>
                            <span
                                className="px-2 py-0.5 rounded text-xs font-semibold text-white"
                                style={{ backgroundColor: SECTOR_COLORS[sector] }}
                            >
                                {sector}
                            </span>
                        </div>
                    </div>

                    {/* Overall Trend Indicator */}
                    <div className={`flex flex-col items-center px-3 py-2 rounded-lg border-2 ${trend.bgColor} ${trend.borderColor}`}>
                        <div className={`${trend.color} mb-1`}>
                            {trend.icon}
                        </div>
                        <span className={`text-xs font-semibold ${trend.color}`}>{trend.label}</span>
                        <span className={`text-lg font-bold ${trend.color}`}>{trend.value}</span>
                    </div>
                </div>
                <p className="text-xs text-gray-500 line-clamp-2">{company.description}</p>
            </div>

            {/* National Indicator Sensitivity with Percentage Bars */}
            <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">National Indicator Sensitivity</h4>
                <div className="space-y-3">
                    {sensitivity_indicators.slice(0, 4).map((indicator, index) => {
                        const percentage = Math.abs(indicator.correlation) * 100;
                        const isPositive = indicator.correlation > 0;

                        return (
                            <div key={index} className="space-y-1">
                                <div className="flex items-center justify-between text-xs">
                                    <span className="font-medium text-gray-700">{indicator.indicator_name}</span>
                                    <div className="flex items-center gap-1">
                                        {isPositive ? (
                                            <ArrowUp className="w-3 h-3 text-green-600" />
                                        ) : (
                                            <ArrowDown className="w-3 h-3 text-red-600" />
                                        )}
                                        <span className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                                            {percentage.toFixed(0)}%
                                        </span>
                                    </div>
                                </div>

                                {/* Percentage Bar */}
                                <div className="relative w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className={`absolute top-0 left-0 h-full rounded-full transition-all ${isPositive ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-red-400 to-red-600'
                                            }`}
                                        style={{ width: `${percentage}%` }}
                                    />
                                </div>

                                <p className="text-xs text-gray-500 italic">{indicator.description}</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Weather/Disaster Impact */}
            {recent_incidents_impact.some(i => i.incident_name.toLowerCase().includes('rain') ||
                i.incident_name.toLowerCase().includes('flood') ||
                i.incident_name.toLowerCase().includes('landslide') ||
                i.incident_name.toLowerCase().includes('weather') ||
                i.incident_name.toLowerCase().includes('drought')) && (
                    <div className="mb-4 p-3 bg-blue-50 border-2 border-blue-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                            <CloudRain className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-semibold text-blue-900">Weather Impact</span>
                        </div>
                        {recent_incidents_impact
                            .filter(i => i.incident_name.toLowerCase().includes('rain') ||
                                i.incident_name.toLowerCase().includes('flood') ||
                                i.incident_name.toLowerCase().includes('landslide') ||
                                i.incident_name.toLowerCase().includes('weather') ||
                                i.incident_name.toLowerCase().includes('drought'))
                            .slice(0, 1)
                            .map((incident, idx) => (
                                <div key={idx} className="space-y-1">
                                    <p className="text-xs font-medium text-blue-900">{incident.incident_name}</p>
                                    <p className="text-xs text-blue-700">{incident.operational_impact}</p>
                                    <div className="flex items-center justify-between mt-2">
                                        <span className="text-xs text-blue-600">Impact: <span className="font-bold">{incident.stock_impact_percent.toFixed(1)}%</span></span>
                                        <span className="text-xs text-blue-600">Recovery: <span className="font-bold">{incident.recovery_days} days</span></span>
                                    </div>
                                </div>
                            ))}
                    </div>
                )}

            {/* Recent National Events Impact */}
            {recent_incidents_impact.length > 0 && (
                <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Recent Events Impact</h4>
                    <div className="space-y-2">
                        {recent_incidents_impact.slice(0, 2).map((incident, index) => (
                            <div key={index} className="p-2 bg-gray-50 rounded border border-gray-200">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-xs font-medium text-gray-900 line-clamp-1">{incident.incident_name}</span>
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${incident.stock_impact_percent >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                        }`}>
                                        {incident.stock_impact_percent >= 0 ? '+' : ''}{incident.stock_impact_percent.toFixed(1)}%
                                    </span>
                                </div>
                                <p className="text-xs text-gray-600">{incident.operational_impact}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Business Insights Summary */}
            <div className="grid grid-cols-2 gap-2">
                <div className="p-2 bg-red-50 rounded border border-red-200">
                    <div className="flex items-center gap-1 mb-1">
                        <AlertTriangle className="w-3 h-3 text-red-600" />
                        <span className="text-xs font-semibold text-red-900">Risks</span>
                    </div>
                    <p className="text-xs text-red-700">{business_insights.risks.length} identified</p>
                </div>

                <div className="p-2 bg-green-50 rounded border border-green-200">
                    <div className="flex items-center gap-1 mb-1">
                        <Lightbulb className="w-3 h-3 text-green-600" />
                        <span className="text-xs font-semibold text-green-900">Opportunities</span>
                    </div>
                    <p className="text-xs text-green-700">{business_insights.opportunities.length} identified</p>
                </div>
            </div>
        </div>
    );
}
