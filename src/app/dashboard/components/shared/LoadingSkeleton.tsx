'use client';

import React from 'react';

interface LoadingSkeletonProps {
    rows?: number;
    variant?: 'default' | 'card' | 'table' | 'stat';
}

export function LoadingSkeleton({ rows = 3, variant = 'default' }: LoadingSkeletonProps) {
    if (variant === 'stat') {
        return (
            <div className="bg-white rounded-xl shadow-lg overflow-hidden animate-pulse">
                <div className="bg-gray-300 h-24"></div>
            </div>
        );
    }

    if (variant === 'card') {
        return (
            <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse space-y-4">
                <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                <div className="h-8 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
        );
    }

    if (variant === 'table') {
        return (
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="animate-pulse">
                    <div className="h-12 bg-gray-300"></div>
                    {Array.from({ length: rows }).map((_, i) => (
                        <div key={i} className="h-16 bg-gray-100 border-t border-gray-200"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="animate-pulse space-y-3">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
        </div>
    );
}

// Full page loading state
export function DashboardLoadingState() {
    return (
        <div className="min-h-screen bg-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Grid Skeleton */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <LoadingSkeleton variant="stat" />
                    <LoadingSkeleton variant="stat" />
                    <LoadingSkeleton variant="stat" />
                    <LoadingSkeleton variant="stat" />
                </div>

                {/* Main Content Skeleton */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <LoadingSkeleton variant="card" />
                    <LoadingSkeleton variant="card" />
                </div>
            </div>
        </div>
    );
}
