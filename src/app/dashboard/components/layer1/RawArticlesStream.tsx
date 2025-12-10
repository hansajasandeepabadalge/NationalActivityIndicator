'use client';

import React, { useState } from 'react';
import { LayerBadge } from '../shared/Badge';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

interface RawArticle {
    article_id: string;
    title: string;
    source_name: string;
    source_url: string;
    scraped_at: string;
    publish_date?: string;
    author?: string;
    word_count?: number;
    language?: string;
}

interface RawArticlesStreamProps {
    articles?: RawArticle[];
    isLoading?: boolean;
    onArticleClick?: (article: RawArticle) => void;
}

export function RawArticlesStream({ articles, isLoading, onArticleClick }: RawArticlesStreamProps) {
    const [selectedSource, setSelectedSource] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [currentPage, setCurrentPage] = useState(1);
    const articlesPerPage = 15;

    // Mock data for development
    const mockArticles: RawArticle[] = [
        {
            article_id: 'art_001',
            title: 'Central Bank Announces New Monetary Policy Measures',
            source_name: 'Daily Mirror',
            source_url: 'https://www.dailymirror.lk/article/123',
            scraped_at: '2 min ago',
            publish_date: '1 hour ago',
            author: 'Economic Desk',
            word_count: 850,
            language: 'en'
        },
        {
            article_id: 'art_002',
            title: 'Government Introduces New Tax Reforms for Small Businesses',
            source_name: 'Economy Next',
            source_url: 'https://economynext.com/article/456',
            scraped_at: '5 min ago',
            publish_date: '2 hours ago',
            author: 'Policy Reporter',
            word_count: 1200,
            language: 'en'
        },
        {
            article_id: 'art_003',
            title: 'Tourism Sector Shows Signs of Recovery',
            source_name: 'Hiru News',
            source_url: 'https://www.hirunews.lk/article/789',
            scraped_at: '8 min ago',
            publish_date: '3 hours ago',
            word_count: 650,
            language: 'si'
        },
        {
            article_id: 'art_004',
            title: 'Stock Market Closes Higher Amid Positive Economic Data',
            source_name: 'Daily Mirror',
            source_url: 'https://www.dailymirror.lk/article/234',
            scraped_at: '12 min ago',
            publish_date: '4 hours ago',
            author: 'Business Desk',
            word_count: 720,
            language: 'en'
        },
        {
            article_id: 'art_005',
            title: 'New Infrastructure Development Projects Announced',
            source_name: 'Government Portal',
            source_url: 'https://www.gov.lk/news/567',
            scraped_at: '15 min ago',
            publish_date: '5 hours ago',
            word_count: 950,
            language: 'en'
        },
        {
            article_id: 'art_006',
            title: 'Fuel Prices Remain Stable Despite Global Market Fluctuations',
            source_name: 'Economy Next',
            source_url: 'https://economynext.com/article/891',
            scraped_at: '20 min ago',
            publish_date: '6 hours ago',
            author: 'Energy Correspondent',
            word_count: 580,
            language: 'en'
        },
    ];

    const displayArticles = articles || mockArticles;

    // Get unique sources for filter
    const uniqueSources = React.useMemo(() => {
        const sources = new Set(displayArticles.map(a => a.source_name));
        return ['all', ...Array.from(sources)];
    }, [displayArticles]);

    // Filter and search logic
    const filteredArticles = React.useMemo(() => {
        let filtered = displayArticles;

        if (selectedSource !== 'all') {
            filtered = filtered.filter(a => a.source_name === selectedSource);
        }

        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(a =>
                a.title.toLowerCase().includes(query) ||
                a.source_name.toLowerCase().includes(query)
            );
        }

        return filtered;
    }, [displayArticles, selectedSource, searchQuery]);

    // Pagination
    const totalPages = Math.ceil(filteredArticles.length / articlesPerPage);
    const startIndex = (currentPage - 1) * articlesPerPage;
    const paginatedArticles = filteredArticles.slice(startIndex, startIndex + articlesPerPage);

    if (isLoading) {
        return <LoadingSkeleton variant="card" rows={8} />;
    }

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">Raw Articles Stream</h3>
                        <LayerBadge layer={1} />
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-600">Live Updates</span>
                    </div>
                </div>

                {/* Filters and Search */}
                <div className="flex flex-col sm:flex-row gap-3">
                    <select
                        value={selectedSource}
                        onChange={(e) => {
                            setSelectedSource(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        {uniqueSources.map(source => (
                            <option key={source} value={source}>
                                {source === 'all' ? 'All Sources' : source}
                            </option>
                        ))}
                    </select>

                    <input
                        type="text"
                        placeholder="Search articles..."
                        value={searchQuery}
                        onChange={(e) => {
                            setSearchQuery(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                <p className="text-sm text-gray-500 mt-2">
                    Showing {filteredArticles.length} article{filteredArticles.length !== 1 ? 's' : ''}
                </p>
            </div>

            {/* Articles List */}
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {paginatedArticles.length > 0 ? (
                    paginatedArticles.map((article) => (
                        <div
                            key={article.article_id}
                            onClick={() => onArticleClick?.(article)}
                            className="p-4 hover:bg-gray-50 cursor-pointer transition"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-medium text-gray-900 mb-1 line-clamp-2">
                                        {article.title}
                                    </h4>
                                    <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                                        <span className="font-medium text-blue-600">{article.source_name}</span>
                                        <span>•</span>
                                        <span>{article.scraped_at}</span>
                                        {article.author && (
                                            <>
                                                <span>•</span>
                                                <span>{article.author}</span>
                                            </>
                                        )}
                                        {article.word_count && (
                                            <>
                                                <span>•</span>
                                                <span>{article.word_count} words</span>
                                            </>
                                        )}
                                        {article.language && article.language !== 'en' && (
                                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded">
                                                {article.language.toUpperCase()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        window.open(article.source_url, '_blank');
                                    }}
                                    className="flex-shrink-0 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
                                >
                                    View Source
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="p-8 text-center text-gray-500">
                        No articles found matching your filters
                    </div>
                )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                        Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                            className="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                            disabled={currentPage === totalPages}
                            className="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
