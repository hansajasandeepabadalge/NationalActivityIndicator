'use client';

import React from 'react';
import { StatusBadge, LayerBadge } from '../shared/Badge';
import { DataTable } from '../shared/DataTable';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

interface ScrapingJob {
    job_id: string;
    source_name: string;
    status: 'running' | 'completed' | 'failed' | 'pending';
    start_time: string;
    end_time?: string;
    duration_seconds?: number;
    articles_found: number;
    articles_processed: number;
    error_message?: string;
}

interface ScrapingJobsPanelProps {
    jobs?: ScrapingJob[];
    isLoading?: boolean;
    onRetry?: (jobId: string) => void;
}

export function ScrapingJobsPanel({ jobs, isLoading, onRetry }: ScrapingJobsPanelProps) {
    // Mock data for development
    const mockJobs: ScrapingJob[] = [
        {
            job_id: 'job_001',
            source_name: 'Daily Mirror',
            status: 'completed',
            start_time: '2 min ago',
            end_time: '1 min ago',
            duration_seconds: 45,
            articles_found: 12,
            articles_processed: 12
        },
        {
            job_id: 'job_002',
            source_name: 'Hiru News',
            status: 'running',
            start_time: '1 min ago',
            articles_found: 8,
            articles_processed: 5
        },
        {
            job_id: 'job_003',
            source_name: 'Economy Next',
            status: 'completed',
            start_time: '10 min ago',
            end_time: '9 min ago',
            duration_seconds: 52,
            articles_found: 6,
            articles_processed: 6
        },
        {
            job_id: 'job_004',
            source_name: 'Ada Derana',
            status: 'failed',
            start_time: '15 min ago',
            end_time: '14 min ago',
            duration_seconds: 15,
            articles_found: 0,
            articles_processed: 0,
            error_message: 'Connection timeout - Unable to reach source server'
        },
        {
            job_id: 'job_005',
            source_name: 'Government Portal',
            status: 'completed',
            start_time: '1 hour ago',
            end_time: '1 hour ago',
            duration_seconds: 28,
            articles_found: 3,
            articles_processed: 3
        },
    ];

    const displayJobs = jobs || mockJobs;

    const columns = [
        {
            key: 'source_name',
            header: 'Source',
            sortable: true,
            render: (job: ScrapingJob) => (
                <div>
                    <p className="font-medium text-gray-900">{job.source_name}</p>
                    <p className="text-xs text-gray-500">{job.job_id}</p>
                </div>
            )
        },
        {
            key: 'status',
            header: 'Status',
            sortable: true,
            render: (job: ScrapingJob) => <StatusBadge status={job.status} />
        },
        {
            key: 'start_time',
            header: 'Time',
            sortable: true,
            render: (job: ScrapingJob) => (
                <div className="text-sm">
                    <p className="text-gray-900">{job.start_time}</p>
                    {job.duration_seconds && (
                        <p className="text-gray-500 text-xs">{job.duration_seconds}s duration</p>
                    )}
                </div>
            )
        },
        {
            key: 'articles_found',
            header: 'Articles',
            sortable: true,
            render: (job: ScrapingJob) => (
                <div className="text-sm">
                    <p className="font-medium text-gray-900">
                        {job.articles_processed}/{job.articles_found}
                    </p>
                    {job.status === 'running' && (
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                            <div
                                className="bg-blue-600 h-1.5 rounded-full transition-all"
                                style={{
                                    width: `${(job.articles_processed / Math.max(job.articles_found, 1)) * 100}%`
                                }}
                            ></div>
                        </div>
                    )}
                </div>
            )
        },
        {
            key: 'actions',
            header: 'Actions',
            render: (job: ScrapingJob) => (
                <div>
                    {job.status === 'failed' && onRetry && (
                        <button
                            onClick={() => onRetry(job.job_id)}
                            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                        >
                            Retry
                        </button>
                    )}
                    {job.error_message && (
                        <button
                            onClick={() => alert(job.error_message)}
                            className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
                        >
                            View Error
                        </button>
                    )}
                </div>
            )
        }
    ];

    const stats = React.useMemo(() => {
        return {
            running: displayJobs.filter(j => j.status === 'running').length,
            completed: displayJobs.filter(j => j.status === 'completed').length,
            failed: displayJobs.filter(j => j.status === 'failed').length,
            total_articles: displayJobs.reduce((sum, j) => sum + j.articles_processed, 0)
        };
    }, [displayJobs]);

    if (isLoading) {
        return <LoadingSkeleton variant="table" rows={5} />;
    }

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Header with stats */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">Scraping Jobs</h3>
                        <LayerBadge layer={1} />
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                        {stats.running > 0 && (
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                                <span className="text-blue-600 font-medium">{stats.running} Running</span>
                            </div>
                        )}
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">Completed:</span>
                            <span className="font-semibold text-green-600">{stats.completed}</span>
                        </div>
                        {stats.failed > 0 && (
                            <div className="flex items-center gap-2">
                                <span className="text-gray-500">Failed:</span>
                                <span className="font-semibold text-red-600">{stats.failed}</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Jobs Table */}
            <DataTable
                data={displayJobs}
                columns={columns}
                keyExtractor={(job) => job.job_id}
                emptyMessage="No scraping jobs found"
                pageSize={10}
            />
        </div>
    );
}
