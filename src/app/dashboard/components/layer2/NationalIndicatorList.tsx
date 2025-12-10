'use client';

import React, { useState } from 'react';
import { TrendArrow, PestelBadge } from '../shared/Badge';
import { useNationalIndicators } from '@/hooks/useDashboard';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

export function NationalIndicatorList() {
    const { data: indicators, isLoading } = useNationalIndicators(undefined, 100);
    const [filter, setFilter] = useState<string>('All');
    const [searchTerm, setSearchTerm] = useState('');

    const categories = ['All', 'Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal', 'Other'];

    const filteredIndicators = React.useMemo(() => {
        if (!indicators) return [];
        return indicators.filter(ind => {
            const matchesCategory = filter === 'All' || ind.pestel_category === filter;
            const matchesSearch = ind.indicator_name.toLowerCase().includes(searchTerm.toLowerCase());
            return matchesCategory && matchesSearch;
        });
    }, [indicators, filter, searchTerm]);

    if (isLoading) return <LoadingSkeleton rows={5} variant="card" />;

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 flex flex-col h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <span>📊</span> National Indicators (Layer 2)
                </h3>
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    {filteredIndicators.length} metrics
                </span>
            </div>

            {/* Controls */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="flex-1">
                    <input
                        type="text"
                        placeholder="Search indicators..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 scrollbar-hide">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setFilter(cat)}
                            className={`
                px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors
                ${filter === cat
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}
              `}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto min-h-[400px] pr-2 space-y-3">
                {filteredIndicators.length > 0 ? (
                    filteredIndicators.map((indicator) => (
                        <div
                            key={indicator.indicator_id}
                            className="group p-4 bg-gray-50/50 hover:bg-white border border-transparent hover:border-gray-200 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <PestelBadge category={indicator.pestel_category || 'Other'} />
                                        <span className="text-xs text-gray-400 font-mono">ID: {indicator.indicator_id.slice(0, 8)}</span>
                                    </div>
                                    <h4 className="font-semibold text-gray-900 truncate" title={indicator.indicator_name}>
                                        {indicator.indicator_name}
                                    </h4>
                                    <p className="text-xs text-gray-500 mt-1 line-clamp-1">{indicator.description || 'No description available'}</p>
                                </div>

                                <div className="text-right flex-shrink-0">
                                    <div className="flex items-center justify-end gap-2 mb-1">
                                        <span className="text-2xl font-bold text-gray-900 tracking-tight">
                                            {indicator.current_value?.toFixed(1) || 'N/A'}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-end gap-1">
                                        <TrendArrow trend={indicator.trend || 'stable'} />
                                        {indicator.change_percentage !== undefined && (
                                            <span className={`text-xs font-medium ${(indicator.change_percentage || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                                }`}>
                                                {indicator.change_percentage > 0 ? '+' : ''}{indicator.change_percentage.toFixed(1)}%
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-12 text-gray-400">
                        No indicators found matching your search.
                    </div>
                )}
            </div>
        </div>
    );
}
