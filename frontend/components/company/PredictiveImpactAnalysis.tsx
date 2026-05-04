'use client';

/**
 * TradingView-Style Predictive Chart
 * Professional financial chart interface
 */

import React, { useState, useMemo } from 'react';
import {
    ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    ReferenceLine, Area, AreaChart
} from 'recharts';
import {
    TrendingUp, TrendingDown, AlertCircle, Brain, ChevronRight,
    Filter, Calendar, Target, Maximize2, TrendingUp as ChartIcon
} from 'lucide-react';
import {
    PREDICTION_SCENARIOS,
    COMPANY_PREDICTIONS,
    getConfidenceColor,
} from '@/data/predictions';

export function PredictiveImpactAnalysis() {
    const [selectedScenario, setSelectedScenario] = useState<string>(PREDICTION_SCENARIOS[0].scenario_id);
    const [selectedCompany, setSelectedCompany] = useState<string>(COMPANY_PREDICTIONS[0].company_id);
    const [timeframe, setTimeframe] = useState<'all' | '30d' | '60d' | '90d'>('all');

    const scenario = PREDICTION_SCENARIOS.find(s => s.scenario_id === selectedScenario);
    const company = COMPANY_PREDICTIONS.find(c => c.company_id === selectedCompany);
    const prediction = company?.predictions.find(p => p.scenario_id === selectedScenario);

    // Get all companies affected by selected scenario
    const affectedCompanies = useMemo(() => {
        return COMPANY_PREDICTIONS.filter(cp =>
            cp.predictions.some(p => p.scenario_id === selectedScenario)
        ).sort((a, b) => {
            const aPred = a.predictions.find(p => p.scenario_id === selectedScenario);
            const bPred = b.predictions.find(p => p.scenario_id === selectedScenario);
            return Math.abs(bPred?.price_change_percent || 0) - Math.abs(aPred?.price_change_percent || 0);
        });
    }, [selectedScenario]);

    // Filter timeline data based on timeframe
    const filteredTimeline = useMemo(() => {
        if (!prediction) return [];
        const maxDays = timeframe === '30d' ? 30 : timeframe === '60d' ? 60 : timeframe === '90d' ? 90 : prediction.timeline[prediction.timeline.length - 1].day;
        return prediction.timeline.filter(p => p.day <= maxDays);
    }, [prediction, timeframe]);

    // Prepare candlestick-style data
    const chartData = useMemo(() => {
        if (!company || !prediction) return [];

        return filteredTimeline.map((point, idx) => {
            const prevPrice = idx > 0 ? filteredTimeline[idx - 1].predicted_price : company.current_price;
            const currentPrice = point.predicted_price;
            const high = Math.max(prevPrice, currentPrice) * (1 + Math.random() * 0.01);
            const low = Math.min(prevPrice, currentPrice) * (1 - Math.random() * 0.01);
            const volume = Math.random() * 1000000 + 500000;

            return {
                day: point.day,
                open: prevPrice,
                close: currentPrice,
                high,
                low,
                volume,
                predicted_price: currentPrice,
                isUp: currentPrice >= prevPrice,
            };
        });
    }, [company, prediction, filteredTimeline]);

    // TradingView-style tooltip
    const TradingViewTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-gray-900 text-white p-3 rounded border border-gray-700 text-xs font-mono">
                    <div className="font-bold mb-2 text-gray-300">Day {data.day}</div>
                    <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-400">O:</span>
                            <span className="text-white">{data.open?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-400">H:</span>
                            <span className="text-green-400">{data.high?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-400">L:</span>
                            <span className="text-red-400">{data.low?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-400">C:</span>
                            <span className={data.isUp ? 'text-green-400' : 'text-red-400'}>
                                {data.close?.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between gap-4 pt-1 border-t border-gray-700">
                            <span className="text-gray-400">Vol:</span>
                            <span className="text-blue-400">{(data.volume / 1000).toFixed(0)}K</span>
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6">
            {/* Compact Header */}
            <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 rounded-lg shadow-xl p-6 text-white">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Brain className="w-8 h-8 text-blue-400" />
                        <div>
                            <h1 className="text-2xl font-bold">Predictive Impact Analysis</h1>
                            <p className="text-gray-400 text-sm">TradingView-style price forecasting</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                        <div className="text-center">
                            <div className="text-gray-400">Scenarios</div>
                            <div className="text-xl font-bold">{PREDICTION_SCENARIOS.length}</div>
                        </div>
                        <div className="text-center">
                            <div className="text-gray-400">Companies</div>
                            <div className="text-xl font-bold">{COMPANY_PREDICTIONS.length}</div>
                        </div>
                    </div>
                </div>

                {/* Future Enhancement Notice - Compact */}
                <div className="mt-4 p-3 bg-yellow-900/30 rounded border border-yellow-600/50 text-xs">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-400" />
                        <span className="text-yellow-200">
                            <strong>Demo Mode:</strong> Mock prediction data • Future: ML models (LSTM/Prophet), real-time data, historical analysis
                        </span>
                    </div>
                </div>
            </div>

            {/* TradingView-Style Layout */}
            <div className="grid grid-cols-12 gap-4">
                {/* Left Sidebar - Scenarios & Companies */}
                <div className="col-span-3 space-y-4">
                    {/* Scenarios */}
                    <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
                        <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            Scenarios
                        </h3>
                        <div className="space-y-2">
                            {PREDICTION_SCENARIOS.map((s) => (
                                <div
                                    key={s.scenario_id}
                                    onClick={() => setSelectedScenario(s.scenario_id)}
                                    className={`p-2 rounded cursor-pointer text-xs transition-all ${selectedScenario === s.scenario_id
                                            ? 'bg-blue-50 border-2 border-blue-500'
                                            : 'border border-gray-200 hover:border-blue-300'
                                        }`}
                                >
                                    <div className="font-semibold text-gray-900 mb-1">{s.scenario_name}</div>
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded font-semibold">
                                            {s.probability}%
                                        </span>
                                        <span>{s.timeframe_days}d</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Companies */}
                    <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
                        <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                            <ChartIcon className="w-4 h-4" />
                            Companies ({affectedCompanies.length})
                        </h3>
                        <div className="space-y-1">
                            {affectedCompanies.map((c) => {
                                const pred = c.predictions.find(p => p.scenario_id === selectedScenario);
                                return (
                                    <div
                                        key={c.company_id}
                                        onClick={() => setSelectedCompany(c.company_id)}
                                        className={`p-2 rounded cursor-pointer text-xs transition-all ${selectedCompany === c.company_id
                                                ? 'bg-blue-50 border-2 border-blue-500'
                                                : 'border border-gray-200 hover:border-blue-300'
                                            }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="font-bold">{c.ticker}</span>
                                            {pred && (
                                                <span className={`font-semibold ${pred.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {pred.price_change_percent > 0 ? '+' : ''}{pred.price_change_percent.toFixed(1)}%
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Main Chart Area - TradingView Style */}
                <div className="col-span-9">
                    {company && prediction && (
                        <div className="bg-white rounded-lg shadow border border-gray-200">
                            {/* Chart Header - TradingView Style */}
                            <div className="border-b border-gray-200 p-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div>
                                            <h2 className="text-xl font-bold text-gray-900">{company.ticker}</h2>
                                            <p className="text-sm text-gray-500">{company.name}</p>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="text-center px-3 py-1 bg-gray-50 rounded">
                                                <div className="text-xs text-gray-500">Current</div>
                                                <div className="text-sm font-bold">{company.current_price.toFixed(2)}</div>
                                            </div>
                                            <div className={`text-center px-3 py-1 rounded ${prediction.price_change_percent > 0 ? 'bg-green-50' : 'bg-red-50'
                                                }`}>
                                                <div className="text-xs text-gray-500">Target</div>
                                                <div className={`text-sm font-bold ${prediction.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
                                                    }`}>
                                                    {prediction.predicted_price.toFixed(2)}
                                                </div>
                                            </div>
                                            <div className={`text-center px-3 py-1 rounded ${prediction.price_change_percent > 0 ? 'bg-green-50' : 'bg-red-50'
                                                }`}>
                                                <div className="text-xs text-gray-500">Change</div>
                                                <div className={`text-sm font-bold ${prediction.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
                                                    }`}>
                                                    {prediction.price_change_percent > 0 ? '+' : ''}{prediction.price_change_percent.toFixed(1)}%
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Timeframe Selector */}
                                    <div className="flex items-center gap-1 bg-gray-100 rounded p-1">
                                        {(['all', '30d', '60d', '90d'] as const).map((tf) => (
                                            <button
                                                key={tf}
                                                onClick={() => setTimeframe(tf)}
                                                className={`px-3 py-1 rounded text-xs font-semibold transition-all ${timeframe === tf
                                                        ? 'bg-white text-blue-600 shadow'
                                                        : 'text-gray-600 hover:text-gray-900'
                                                    }`}
                                            >
                                                {tf.toUpperCase()}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Main Chart - TradingView Style */}
                            <div className="p-4">
                                <div className="h-96 bg-gray-50 rounded border border-gray-200">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                            <defs>
                                                <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                                                </linearGradient>
                                            </defs>

                                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />

                                            <XAxis
                                                dataKey="day"
                                                tick={{ fontSize: 11, fill: '#6b7280' }}
                                                axisLine={{ stroke: '#d1d5db' }}
                                                tickLine={{ stroke: '#d1d5db' }}
                                            />

                                            <YAxis
                                                yAxisId="price"
                                                orientation="right"
                                                tick={{ fontSize: 11, fill: '#6b7280' }}
                                                axisLine={{ stroke: '#d1d5db' }}
                                                tickLine={{ stroke: '#d1d5db' }}
                                                domain={['auto', 'auto']}
                                            />

                                            <YAxis
                                                yAxisId="volume"
                                                orientation="left"
                                                tick={{ fontSize: 11, fill: '#6b7280' }}
                                                axisLine={false}
                                                tickLine={false}
                                                domain={[0, 'auto']}
                                            />

                                            <Tooltip content={<TradingViewTooltip />} />

                                            {/* Current Price Reference Line */}
                                            <ReferenceLine
                                                yAxisId="price"
                                                y={company.current_price}
                                                stroke="#6b7280"
                                                strokeDasharray="3 3"
                                                strokeWidth={1}
                                            />

                                            {/* Volume Bars */}
                                            <Bar
                                                yAxisId="volume"
                                                dataKey="volume"
                                                fill="url(#volumeGradient)"
                                                opacity={0.5}
                                            />

                                            {/* Price Line */}
                                            <Line
                                                yAxisId="price"
                                                type="monotone"
                                                dataKey="predicted_price"
                                                stroke={prediction.price_change_percent > 0 ? "#10b981" : "#ef4444"}
                                                strokeWidth={2}
                                                dot={false}
                                                activeDot={{ r: 4, fill: prediction.price_change_percent > 0 ? "#10b981" : "#ef4444" }}
                                            />
                                        </ComposedChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Chart Footer - Confidence & Drivers */}
                            <div className="border-t border-gray-200 p-4 bg-gray-50">
                                <div className="grid grid-cols-2 gap-4">
                                    {/* Confidence */}
                                    <div>
                                        <div className="flex items-center gap-2 mb-2">
                                            <Target className="w-4 h-4 text-gray-600" />
                                            <span className="text-sm font-semibold text-gray-700">Confidence Level</span>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full ${prediction.confidence_level === 'high' ? 'bg-green-500' :
                                                            prediction.confidence_level === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
                                                        }`}
                                                    style={{ width: `${prediction.confidence_score}%` }}
                                                />
                                            </div>
                                            <span className={`text-sm font-bold ${getConfidenceColor(prediction.confidence_level)}`}>
                                                {prediction.confidence_score}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* Key Drivers */}
                                    <div>
                                        <div className="flex items-center gap-2 mb-2">
                                            <ChevronRight className="w-4 h-4 text-gray-600" />
                                            <span className="text-sm font-semibold text-gray-700">Key Drivers</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {prediction.key_drivers.slice(0, 2).join(' • ')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
