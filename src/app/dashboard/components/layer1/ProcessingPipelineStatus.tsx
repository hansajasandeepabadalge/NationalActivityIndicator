'use client';

import React from 'react';
import { LayerBadge, StatusBadge } from '../shared/Badge';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

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

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">Processing Pipeline Status</h3>
                        <LayerBadge layer={1} />
                    </div>
                    <StatusBadge status={stats.overall_success_rate >= 95 ? 'active' : 'pending'} label="Pipeline Health" />
                </div>

                {/* Overall Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-600 font-medium">Overall Success</p>
                        <p className="text-2xl font-bold text-blue-700 mt-1">
                            {stats.overall_success_rate.toFixed(1)}%
                        </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs text-green-600 font-medium">Throughput</p>
                        <p className="text-2xl font-bold text-green-700 mt-1">
                            {stats.current_throughput}/hr
                        </p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-3">
                        <p className="text-xs text-yellow-600 font-medium">Avg Processing</p>
                        <p className="text-2xl font-bold text-yellow-700 mt-1">
                            {stats.avg_processing_time.toFixed(1)}s
                        </p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-3">
                        <p className="text-xs text-red-600 font-medium">Total Errors</p>
                        <p className="text-2xl font-bold text-red-700 mt-1">
                            {stats.total_errors.toLocaleString()}
                        </p>
                    </div>
                </div>
            </div>

            {/* Pipeline Funnel Visualization */}
            <div className="p-6">
                <div className="space-y-4">
                    {displayStages.map((stage, index) => {
                        const prevStage = index > 0 ? displayStages[index - 1] : null;
                        const dropoff = prevStage ? prevStage.count - stage.count : 0;
                        const dropoff_percentage = prevStage ? (dropoff / prevStage.count) * 100 : 0;
                        const width_percentage = (stage.count / displayStages[0].count) * 100;

                        return (
                            <div key={stage.name} className="relative">
                                {/* Stage Card */}
                                <div
                                    className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white transition-all hover:shadow-lg"
                                    style={{ width: `${width_percentage}%`, minWidth: '60%' }}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className="font-semibold text-lg">{stage.name}</h4>
                                        <div className="flex items-center gap-4 text-sm">
                                            <span className="bg-white/20 px-2 py-1 rounded">
                                                {stage.count.toLocaleString()} articles
                                            </span>
                                            <span className="bg-white/20 px-2 py-1 rounded">
                                                {stage.processing_rate}/hr
                                            </span>
                                        </div>
                                    </div>

                                    {/* Stage Stats */}
                                    <div className="grid grid-cols-3 gap-3 text-sm">
                                        <div>
                                            <p className="text-blue-100 text-xs">Success Rate</p>
                                            <p className="font-medium">{stage.success_rate.toFixed(1)}%</p>
                                        </div>
                                        <div>
                                            <p className="text-blue-100 text-xs">Avg Time</p>
                                            <p className="font-medium">{stage.avg_processing_time.toFixed(1)}s</p>
                                        </div>
                                        <div>
                                            <p className="text-blue-100 text-xs">Errors</p>
                                            <p className="font-medium">{stage.error_count.toLocaleString()}</p>
                                        </div>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="mt-3 bg-white/20 rounded-full h-2 overflow-hidden">
                                        <div
                                            className="bg-white h-full rounded-full transition-all"
                                            style={{ width: `${stage.success_rate}%` }}
                                        ></div>
                                    </div>
                                </div>

                                {/* Dropoff Indicator */}
                                {dropoff > 0 && (
                                    <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-medium border border-red-200">
                                        ↓ {dropoff.toLocaleString()} ({dropoff_percentage.toFixed(1)}%) dropped
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Bottleneck Alert */}
                {stats.overall_success_rate < 95 && (
                    <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">⚠️</span>
                            <div>
                                <h4 className="font-semibold text-yellow-900 mb-1">Pipeline Bottleneck Detected</h4>
                                <p className="text-sm text-yellow-700">
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
