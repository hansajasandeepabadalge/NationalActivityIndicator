'use client';

import React from 'react';
import { NationalIndicatorList } from './NationalIndicatorList';
import { OperationalMetricsGrid } from './OperationalMetricsGrid';
import { BusinessInsightsPanel } from './BusinessInsightsPanel';

export function IndicatorAnalysis() {
    return (
        <div className="space-y-6 animate-in fade-in duration-500 slide-in-from-bottom-2">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Indicators & Analysis</h2>
                    <p className="text-gray-500 mt-1">Deep dive into national indicators (L2), operational metrics (L3), and strategic insights (L4).</p>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 shadow-sm transition-colors">
                        Export Report
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shadow-sm transition-colors shadow-blue-200">
                        Refresh Data
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 h-[calc(100vh-250px)] min-h-[800px]">
                {/* Left Column: National Indicators (L2) - 5 cols */}
                <div className="xl:col-span-5 h-full">
                    <NationalIndicatorList />
                </div>

                {/* Right Column: Split Top/Bottom - 7 cols */}
                <div className="xl:col-span-7 flex flex-col gap-6 h-full">
                    {/* Top: Operational Metrics (L3) */}
                    <div className="flex-1 min-h-0">
                        <OperationalMetricsGrid />
                    </div>

                    {/* Bottom: Business Insights (L4) */}
                    <div className="flex-1 min-h-0">
                        <BusinessInsightsPanel />
                    </div>
                </div>
            </div>
        </div>
    );
}
