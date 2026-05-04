'use client';

import React from 'react';
import { StatusBadge, LayerBadge } from '../shared/Badge';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

interface DataSource {
    id: number;
    name: string;
    display_name: string;
    source_type: 'news' | 'government' | 'social_media' | 'api';
    status: 'active' | 'inactive' | 'error';
    base_url: string;
    last_scraped?: string;
    total_articles: number;
    articles_24h: number;
    success_rate: number;
    avg_articles_per_scrape: number;
}

interface DataSourcesMonitorProps {
    sources?: DataSource[];
    isLoading?: boolean;
    onSourceClick?: (source: DataSource) => void;
}

export function DataSourcesMonitor({ sources, isLoading, onSourceClick }: DataSourcesMonitorProps) {
    const [filterType, setFilterType] = React.useState<string>('all');
    const [sortBy, setSortBy] = React.useState<'name' | 'articles' | 'last_scraped'>('name');

    // Mock data for development
    const mockSources: DataSource[] = [
        {
            id: 1,
            name: 'daily_mirror',
            display_name: 'Daily Mirror',
            source_type: 'news',
            status: 'active',
            base_url: 'https://www.dailymirror.lk',
            last_scraped: '2 min ago',
            total_articles: 15420,
            articles_24h: 48,
            success_rate: 96.5,
            avg_articles_per_scrape: 12
        },
        {
            id: 2,
            name: 'hiru_news',
            display_name: 'Hiru News',
            source_type: 'news',
            status: 'active',
            base_url: 'https://www.hirunews.lk',
            last_scraped: '5 min ago',
            total_articles: 12300,
            articles_24h: 35,
            success_rate: 94.2,
            avg_articles_per_scrape: 10
        },
        {
            id: 3,
            name: 'government_portal',
            display_name: 'Government Portal',
            source_type: 'government',
            status: 'active',
            base_url: 'https://www.gov.lk',
            last_scraped: '1 hour ago',
            total_articles: 2150,
            articles_24h: 5,
            success_rate: 100,
            avg_articles_per_scrape: 3
        },
        {
            id: 4,
            name: 'economynext',
            display_name: 'Economy Next',
            source_type: 'news',
            status: 'active',
            base_url: 'https://economynext.com',
            last_scraped: '15 min ago',
            total_articles: 8900,
            articles_24h: 22,
            success_rate: 91.8,
            avg_articles_per_scrape: 8
        },
        {
            id: 5,
            name: 'cbsl',
            display_name: 'Central Bank of Sri Lanka',
            source_type: 'government',
            status: 'active',
            base_url: 'https://www.cbsl.gov.lk',
            last_scraped: '2 hours ago',
            total_articles: 580,
            articles_24h: 2,
            success_rate: 100,
            avg_articles_per_scrape: 2
        },
        {
            id: 6,
            name: 'ada_derana',
            display_name: 'Ada Derana',
            source_type: 'news',
            status: 'error',
            base_url: 'https://www.adaderana.lk',
            last_scraped: '3 days ago',
            total_articles: 18500,
            articles_24h: 0,
            success_rate: 0,
            avg_articles_per_scrape: 15
        },
    ];

    const displaySources = sources || mockSources;

    // Filter logic
    const filteredSources = React.useMemo(() => {
        let filtered = displaySources;

        if (filterType !== 'all') {
            filtered = filtered.filter(s => s.source_type === filterType);
        }

        // Sort
        return [...filtered].sort((a, b) => {
            if (sortBy === 'name') {
                return a.display_name.localeCompare(b.display_name);
            } else if (sortBy === 'articles') {
                return b.articles_24h - a.articles_24h;
            } else {
                return 0; // last_scraped would need parsing
            }
        });
    }, [displaySources, filterType, sortBy]);

    const stats = React.useMemo(() => {
        return {
            total: displaySources.length,
            active: displaySources.filter(s => s.status === 'active').length,
            total_articles_24h: displaySources.reduce((sum, s) => sum + s.articles_24h, 0),
            avg_success_rate: displaySources.length > 0
                ? displaySources.reduce((sum, s) => sum + s.success_rate, 0) / displaySources.length
                : 0
        };
    }, [displaySources]);

    if (isLoading) {
        return <LoadingSkeleton variant="card" rows={6} />;
    }

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">Data Sources Monitor</h3>
                        <LayerBadge layer={1} />
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">Total:</span>
                            <span className="font-semibold text-gray-900">{stats.total}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">Active:</span>
                            <span className="font-semibold text-green-600">{stats.active}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">24h Articles:</span>
                            <span className="font-semibold text-blue-600">{stats.total_articles_24h}</span>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="flex items-center gap-4">
                    <div className="flex gap-2">
                        {['all', 'news', 'government', 'social_media', 'api'].map((type) => (
                            <button
                                key={type}
                                onClick={() => setFilterType(type)}
                                className={`px-3 py-1 text-sm rounded-lg transition ${filterType === type
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {type === 'all' ? 'All' : type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </button>
                        ))}
                    </div>
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as any)}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="name">Sort by Name</option>
                        <option value="articles">Sort by Articles (24h)</option>
                        <option value="last_scraped">Sort by Last Scraped</option>
                    </select>
                </div>
            </div>

            {/* Sources Grid */}
            <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredSources.map((source) => (
                        <div
                            key={source.id}
                            onClick={() => onSourceClick?.(source)}
                            className={`p-4 border-2 rounded-lg transition cursor-pointer ${source.status === 'active'
                                    ? 'border-green-200 bg-green-50 hover:border-green-300'
                                    : source.status === 'error'
                                        ? 'border-red-200 bg-red-50 hover:border-red-300'
                                        : 'border-gray-200 bg-gray-50 hover:border-gray-300'
                                }`}
                        >
                            {/* Source Header */}
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-gray-900 truncate" title={source.display_name}>
                                        {source.display_name}
                                    </h4>
                                    <p className="text-xs text-gray-500 truncate" title={source.base_url}>
                                        {source.base_url}
                                    </p>
                                </div>
                                <StatusBadge status={source.status} />
                            </div>

                            {/* Source Stats */}
                            <div className="grid grid-cols-2 gap-2 text-sm">
                                <div>
                                    <p className="text-gray-500 text-xs">Last Scraped</p>
                                    <p className="font-medium text-gray-900">{source.last_scraped || 'Never'}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500 text-xs">24h Articles</p>
                                    <p className="font-medium text-blue-600">{source.articles_24h}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500 text-xs">Total Articles</p>
                                    <p className="font-medium text-gray-900">{source.total_articles.toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500 text-xs">Success Rate</p>
                                    <p className={`font-medium ${source.success_rate >= 95 ? 'text-green-600' : source.success_rate >= 80 ? 'text-yellow-600' : 'text-red-600'}`}>
                                        {source.success_rate.toFixed(1)}%
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
