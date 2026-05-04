'use client';

/**
 * Colombo Stock Exchange Widget
 * 
 * Displays CSE market summary, indices, and top movers
 */

import React, { useEffect, useState } from 'react';
import { StockService } from '@/lib/services/stockService';
import { CSEData } from '@/types/stock';
import { TrendingUp, TrendingDown, RefreshCw, BarChart3, ArrowUp, ArrowDown } from 'lucide-react';

export function ColomboStockExchangeWidget() {
    const [cseData, setCSEData] = useState<CSEData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    const fetchStockData = async () => {
        setIsLoading(true);
        try {
            const data = await StockService.getMarketSummary();
            setCSEData(data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error('Failed to fetch CSE data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchStockData();

        // Auto-refresh every 5 minutes
        const interval = setInterval(fetchStockData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const handleRefresh = () => {
        StockService.clearCache();
        fetchStockData();
    };

    if (isLoading && !cseData) {
        return (
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <div className="flex items-center justify-center h-64">
                    <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
            </div>
        );
    }

    if (!cseData) return null;

    const aspi = cseData.indices.find(i => i.code === 'ASPI');
    const sp20 = cseData.indices.find(i => i.code === 'S&P SL20');

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-600 rounded-lg">
                            <BarChart3 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Colombo Stock Exchange</h3>
                            <p className="text-sm text-gray-600">
                                {lastUpdate ? `Updated: ${lastUpdate.toLocaleTimeString()}` : 'Loading...'}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Main Indices */}
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* ASPI */}
                {aspi && (
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5 border-2 border-blue-200">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-blue-700">{aspi.name}</span>
                            <span className="text-xs font-bold text-blue-600 bg-white px-2 py-1 rounded">{aspi.code}</span>
                        </div>
                        <div className="flex items-baseline gap-3 mb-2">
                            <span className="text-3xl font-bold text-gray-900">{aspi.value.toFixed(2)}</span>
                            <div className={`flex items-center gap-1 ${aspi.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {aspi.change >= 0 ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                                <span className="text-lg font-semibold">
                                    {aspi.change >= 0 ? '+' : ''}{aspi.change.toFixed(2)} ({aspi.changePercent.toFixed(2)}%)
                                </span>
                            </div>
                        </div>
                        <div className="flex justify-between text-sm text-gray-600">
                            <span>High: <strong>{aspi.high.toFixed(2)}</strong></span>
                            <span>Low: <strong>{aspi.low.toFixed(2)}</strong></span>
                        </div>
                    </div>
                )}

                {/* S&P SL20 */}
                {sp20 && (
                    <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-5 border-2 border-indigo-200">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-indigo-700">{sp20.name}</span>
                            <span className="text-xs font-bold text-indigo-600 bg-white px-2 py-1 rounded">{sp20.code}</span>
                        </div>
                        <div className="flex items-baseline gap-3 mb-2">
                            <span className="text-3xl font-bold text-gray-900">{sp20.value.toFixed(2)}</span>
                            <div className={`flex items-center gap-1 ${sp20.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {sp20.change >= 0 ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                                <span className="text-lg font-semibold">
                                    {sp20.change >= 0 ? '+' : ''}{sp20.change.toFixed(2)} ({sp20.changePercent.toFixed(2)}%)
                                </span>
                            </div>
                        </div>
                        <div className="flex justify-between text-sm text-gray-600">
                            <span>High: <strong>{sp20.high.toFixed(2)}</strong></span>
                            <span>Low: <strong>{sp20.low.toFixed(2)}</strong></span>
                        </div>
                    </div>
                )}
            </div>

            {/* Market Summary */}
            <div className="px-6 pb-6">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Market Summary</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Turnover</p>
                        <p className="text-lg font-bold text-gray-900">{StockService.formatCurrency(cseData.marketSummary.totalTurnover)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Volume</p>
                        <p className="text-lg font-bold text-gray-900">{StockService.formatVolume(cseData.marketSummary.totalVolume)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Trades</p>
                        <p className="text-lg font-bold text-gray-900">{cseData.marketSummary.totalTrades.toLocaleString()}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Market Cap</p>
                        <p className="text-lg font-bold text-gray-900">LKR {cseData.marketSummary.marketCap}T</p>
                    </div>
                </div>

                {/* Advancers/Decliners */}
                <div className="grid grid-cols-3 gap-3 mt-3">
                    <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                        <p className="text-xs text-green-700 mb-1">Advancers</p>
                        <p className="text-2xl font-bold text-green-600">{cseData.marketSummary.advancers}</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                        <p className="text-xs text-red-700 mb-1">Decliners</p>
                        <p className="text-2xl font-bold text-red-600">{cseData.marketSummary.decliners}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Unchanged</p>
                        <p className="text-2xl font-bold text-gray-900">{cseData.marketSummary.unchanged}</p>
                    </div>
                </div>
            </div>

            {/* Top Movers */}
            <div className="p-6 bg-gray-50 border-t border-gray-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Top Gainers */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingUp className="w-4 h-4 text-green-600" />
                            <h4 className="text-sm font-semibold text-gray-900">Top Gainers</h4>
                        </div>
                        <div className="space-y-2">
                            {cseData.topGainers.slice(0, 3).map((stock) => (
                                <div key={stock.symbol} className="bg-white rounded-lg p-3 border border-gray-200">
                                    <div className="flex justify-between items-start mb-1">
                                        <div>
                                            <p className="font-bold text-gray-900">{stock.symbol}</p>
                                            <p className="text-xs text-gray-600 truncate">{stock.name}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-gray-900">LKR {stock.price.toFixed(2)}</p>
                                            <p className="text-xs text-green-600 font-semibold">+{stock.changePercent.toFixed(2)}%</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Top Losers */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingDown className="w-4 h-4 text-red-600" />
                            <h4 className="text-sm font-semibold text-gray-900">Top Losers</h4>
                        </div>
                        <div className="space-y-2">
                            {cseData.topLosers.slice(0, 3).map((stock) => (
                                <div key={stock.symbol} className="bg-white rounded-lg p-3 border border-gray-200">
                                    <div className="flex justify-between items-start mb-1">
                                        <div>
                                            <p className="font-bold text-gray-900">{stock.symbol}</p>
                                            <p className="text-xs text-gray-600 truncate">{stock.name}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-gray-900">LKR {stock.price.toFixed(2)}</p>
                                            <p className="text-xs text-red-600 font-semibold">{stock.changePercent.toFixed(2)}%</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
