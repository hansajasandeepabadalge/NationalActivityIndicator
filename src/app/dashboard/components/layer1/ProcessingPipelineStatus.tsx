'use client';

import React from 'react';
import { LayerBadge, StatusBadge } from '../shared/Badge';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';
import { CheckCircle2, AlertTriangle, Clock, TrendingUp } from 'lucide-react';

interface PipelineStage {
    name: string;
    count: number;
    processing_rate: number; // articles per hour
    success_rate: number;
    error_count: number;
    avg_processing_time: number; // seconds
}

interface ProcessingPipelineStatusProps {
    stages?: PipelineStage[];
    isLoading?: boolean;
}

export function ProcessingPipelineStatus({ stages, isLoading }: ProcessingPipelineStatusProps) {
    // Mock data for development
    const mockStages: PipelineStage[] = [
        {
            name: 'Raw Scraped',
            count: 45280,
            processing_rate: 124,
            success_rate: 100,
            error_count: 0,
            avg_processing_time: 0
        },
        {
            name: 'Validated',
            count: 44870,
            processing_rate: 122,
            success_rate: 99.1,
            error_count: 410,
            avg_processing_time: 0.8
        },
        {
            name: 'Translated',
            count: 42150,
            processing_rate: 98,
            success_rate: 94.0,
            error_count: 2720,
            avg_processing_time: 2.5
        },
        {
            name: 'Cleaned',
            count: 41890,
            processing_rate: 96,
            success_rate: 99.4,
            error_count: 260,
            avg_processing_time: 1.2
        },
        {
            name: 'Processed',
            count: 41620,
            processing_rate: 95,
            success_rate: 99.4,
            error_count: 270,
            avg_processing_time: 3.5
        }
    ];

    const displayStages = stages || mockStages;

    // Calculate overall stats
    const stats = React.useMemo(() => {
        const first = displayStages[0];
        const last = displayStages[displayStages.length - 1];
        const overall_success_rate = first ? (last.count / first.count) * 100 : 0;
        const total_errors = displayStages.reduce((sum, stage) => sum + stage.error_count, 0);
        const avg_processing_time = displayStages.reduce((sum, stage) => sum + stage.avg_processing_time, 0);

        return {
            overall_success_rate,
            total_errors,
            avg_processing_time,
            current_throughput: last?.processing_rate || 0
        };
    }, [displayStages]);

    if (isLoading) {
        return <LoadingSkeleton variant="card" rows={5} />;
    }

    const getStageAccentColor = (index: number) => {
        const colors = [
            { border: 'border-blue-200', bg: 'bg-blue-50', text: 'text-blue-700', accent: 'bg-blue-500' },
            { border: 'border-indigo-200', bg: 'bg-indigo-50', text: 'text-indigo-700', accent: 'bg-indigo-500' },
            { border: 'border-purple-200', bg: 'bg-purple-50', text: 'text-purple-700', accent: 'bg-purple-500' },
            { border: 'border-pink-200', bg: 'bg-pink-50', text: 'text-pink-700', accent: 'bg-pink-500' },
            { border: 'border-rose-200', bg: 'bg-rose-50', text: 'text-rose-700', accent: 'bg-rose-500' }
        ];
        return colors[index % colors.length];
    };

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
            {/* Header */}
            <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 rounded-lg border border-blue-100">
                            <TrendingUp className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Processing Pipeline Status</h3>
                            <p className="text-sm text-gray-500">Real-time data flow monitoring</p>
                        </div>
                    </div>
                    <LayerBadge layer={1} />
                </div>

                {/* Overall Stats - Clean White Cards with Subtle Accents */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white border-2 border-blue-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-1.5 bg-blue-50 rounded-lg">
                                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                            </div>
                            <p className="text-xs text-gray-600 font-medium">Overall Success</p>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                            {stats.overall_success_rate.toFixed(1)}<span className="text-lg text-blue-600">%</span>
                        </p>
                    </div>

                    <div className="bg-white border-2 border-green-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-1.5 bg-green-50 rounded-lg">
                                <TrendingUp className="w-4 h-4 text-green-600" />
                            </div>
                            <p className="text-xs text-gray-600 font-medium">Throughput</p>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                            {stats.current_throughput}<span className="text-lg text-green-600">/hr</span>
                        </p>
                    </div>

                    <div className="bg-white border-2 border-amber-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-1.5 bg-amber-50 rounded-lg">
                                <Clock className="w-4 h-4 text-amber-600" />
                            </div>
                            <p className="text-xs text-gray-600 font-medium">Avg Processing</p>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                            {stats.avg_processing_time.toFixed(1)}<span className="text-lg text-amber-600">s</span>
                        </p>
                    </div>

                    <div className="bg-white border-2 border-red-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-1.5 bg-red-50 rounded-lg">
                                <AlertTriangle className="w-4 h-4 text-red-600" />
                            </div>
                            <p className="text-xs text-gray-600 font-medium">Total Errors</p>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                            {stats.total_errors.toLocaleString()}
                        </p>
                    </div>
                </div>
            </div>

            {/* Pipeline Stages - Clean White Design */}
            <div className="p-6 bg-gray-50">
                <div className="space-y-3">
                    {displayStages.map((stage, index) => {
                        const prevStage = index > 0 ? displayStages[index - 1] : null;
                        const dropoff = prevStage ? prevStage.count - stage.count : 0;
                        const dropoff_percentage = prevStage ? (dropoff / prevStage.count) * 100 : 0;
                        const width_percentage = (stage.count / displayStages[0].count) * 100;
                        const colors = getStageAccentColor(index);

                        return (
                            <div key={stage.name} className="relative">
                                {/* Clean White Stage Card */}
                                <div
                                    className={`relative bg-white border-2 ${colors.border} rounded-xl p-5 hover:shadow-lg transition-all duration-300`}
                                    style={{ width: `${Math.max(width_percentage, 70)}%` }}
                                >
                                    {/* Accent bar on left */}
                                    <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${colors.accent} rounded-l-xl`}></div>

                                    <div className="pl-3">
                                        {/* Header */}
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-10 h-10 ${colors.bg} backdrop-blur-sm rounded-lg flex items-center justify-center border ${colors.border}`}>
                                                    <span className={`text-lg font-bold ${colors.text}`}>{index + 1}</span>
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-lg text-gray-900">{stage.name}</h4>
                                                    <p className="text-sm text-gray-600">{stage.count.toLocaleString()} articles</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className={`${colors.bg} border ${colors.border} px-3 py-1.5 rounded-lg`}>
                                                    <p className={`text-sm font-semibold ${colors.text}`}>{stage.processing_rate}/hr</p>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Stats Grid */}
                                        <div className="grid grid-cols-3 gap-4 mb-3">
                                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                                                <p className="text-xs text-gray-500 mb-1">Success Rate</p>
                                                <p className="text-xl font-bold text-gray-900">{stage.success_rate.toFixed(1)}%</p>
                                            </div>
                                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                                                <p className="text-xs text-gray-500 mb-1">Avg Time</p>
                                                <p className="text-xl font-bold text-gray-900">{stage.avg_processing_time.toFixed(1)}s</p>
                                            </div>
                                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                                                <p className="text-xs text-gray-500 mb-1">Errors</p>
                                                <p className="text-xl font-bold text-gray-900">{stage.error_count.toLocaleString()}</p>
                                            </div>
                                        </div>

                                        {/* Progress Bar */}
                                        <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                                            <div
                                                className={`${colors.accent} h-full rounded-full transition-all duration-500`}
                                                style={{ width: `${stage.success_rate}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </div>

                                {/* Dropoff Indicator */}
                                {dropoff > 0 && (
                                    <div className="flex items-center justify-center mt-2 mb-1">
                                        <div className="bg-white border-2 border-red-200 text-red-700 px-4 py-1.5 rounded-full text-sm font-medium shadow-sm flex items-center gap-2">
                                            <span className="text-red-500">↓</span>
                                            {dropoff.toLocaleString()} dropped ({dropoff_percentage.toFixed(1)}%)
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Bottleneck Alert - Clean Design */}
                {stats.overall_success_rate < 95 && (
                    <div className="mt-6 bg-white border-2 border-amber-200 rounded-xl p-5 shadow-sm">
                        <div className="flex items-start gap-4">
                            <div className="p-2 bg-amber-50 rounded-lg border border-amber-200">
                                <AlertTriangle className="w-6 h-6 text-amber-600" />
                            </div>
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900 mb-2 text-lg">Pipeline Bottleneck Detected</h4>
                                <p className="text-sm text-gray-600 leading-relaxed">
                                    Overall success rate is below 95%. Check individual stage error counts and processing times for optimization opportunities.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
