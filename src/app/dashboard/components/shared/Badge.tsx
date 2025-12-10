'use client';

import React from 'react';

// PESTEL Category Badge
interface PestelBadgeProps {
    category: string;
}

export function PestelBadge({ category }: PestelBadgeProps) {
    const colors: Record<string, string> = {
        Political: 'bg-red-100 text-red-800 border-red-200',
        Economic: 'bg-blue-100 text-blue-800 border-blue-200',
        Social: 'bg-green-100 text-green-800 border-green-200',
        Technological: 'bg-purple-100 text-purple-800 border-purple-200',
        Environmental: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        Legal: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[category] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
            {category}
        </span>
    );
}

// Severity/Priority Badge
interface SeverityBadgeProps {
    level: 'critical' | 'high' | 'medium' | 'low';
    label?: string;
}

export function SeverityBadge({ level, label }: SeverityBadgeProps) {
    const colors: Record<string, string> = {
        critical: 'bg-red-100 text-red-800 border-red-300',
        high: 'bg-orange-100 text-orange-800 border-orange-300',
        medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        low: 'bg-green-100 text-green-800 border-green-300',
    };

    return (
        <span className={`px-2 py-1 rounded-md text-xs font-medium border ${colors[level]}`}>
            {label || level.toUpperCase()}
        </span>
    );
}

// Status Badge
interface StatusBadgeProps {
    status: 'active' | 'inactive' | 'running' | 'completed' | 'failed' | 'pending' | 'error';
    label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
    const colors: Record<string, string> = {
        active: 'bg-green-100 text-green-800 border-green-300',
        inactive: 'bg-gray-100 text-gray-800 border-gray-300',
        running: 'bg-blue-100 text-blue-800 border-blue-300 animate-pulse',
        completed: 'bg-green-100 text-green-800 border-green-300',
        failed: 'bg-red-100 text-red-800 border-red-300',
        pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        error: 'bg-red-100 text-red-800 border-red-300',
    };

    return (
        <span className={`px-2 py-1 rounded-md text-xs font-medium border ${colors[status]}`}>
            {label || status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
}

// Trend Arrow
interface TrendArrowProps {
    trend: 'up' | 'down' | 'stable';
    showLabel?: boolean;
}

export function TrendArrow({ trend, showLabel = false }: TrendArrowProps) {
    const arrows = {
        up: { symbol: '↑', color: 'text-green-500', label: 'Increasing' },
        down: { symbol: '↓', color: 'text-red-500', label: 'Decreasing' },
        stable: { symbol: '→', color: 'text-gray-400', label: 'Stable' },
    };

    const arrow = arrows[trend];

    return (
        <span className={`inline-flex items-center gap-1 ${arrow.color} font-semibold`}>
            {arrow.symbol}
            {showLabel && <span className="text-xs">{arrow.label}</span>}
        </span>
    );
}

// Layer Badge (for identifying which layer data comes from)
interface LayerBadgeProps {
    layer: 1 | 2 | 3 | 4 | 5;
}

export function LayerBadge({ layer }: LayerBadgeProps) {
    const colors: Record<number, string> = {
        1: 'bg-purple-100 text-purple-800',
        2: 'bg-blue-100 text-blue-800',
        3: 'bg-green-100 text-green-800',
        4: 'bg-yellow-100 text-yellow-800',
        5: 'bg-pink-100 text-pink-800',
    };

    const labels: Record<number, string> = {
        1: 'Layer 1',
        2: 'Layer 2',
        3: 'Layer 3',
        4: 'Layer 4',
        5: 'Layer 5',
    };

    return (
        <span className={`px-2 py-1 ${colors[layer]} text-xs font-medium rounded`}>
            {labels[layer]}
        </span>
    );
}
